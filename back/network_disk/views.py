"""
网盘文件管理视图
公共网盘，使用用户ID作为文件夹名（但显示用户名）
权限控制：
- 根目录：只读，不能上传删除
- 自己的文件夹：完全权限（需要登录）
- 其他人的文件夹：只读，可以下载
- 访客：只能下载，不能上传删除
"""
import os
import json
from pathlib import Path
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from common.jwt_utils import jwt_required
from django.db import connection


# 网盘文件根目录
NETWORK_DISK_ROOT = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'


def get_username_by_id(user_id):
    """通过用户ID获取用户名"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE id = %s", [user_id])
            row = cursor.fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    return None


def get_user_id_by_username(username):
    """通过用户名获取用户ID"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", [username])
            row = cursor.fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    return None


def ensure_user_directory(user_id):
    """确保用户目录存在，如果不存在则创建"""
    user_dir = NETWORK_DISK_ROOT / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_file_info(file_path):
    """获取文件信息"""
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified_time': stat.st_mtime,
        'is_directory': file_path.is_dir(),
    }


def check_path_safety(path, base_path):
    """检查路径安全性，确保路径在base_path内"""
    try:
        resolved_path = path.resolve()
        resolved_base = base_path.resolve()
        return str(resolved_path).startswith(str(resolved_base))
    except (OSError, ValueError):
        return False


def get_path_owner_id(path_parts):
    """从路径中提取所有者用户ID（第一个路径部分）"""
    if not path_parts or len(path_parts) == 0:
        return None
    try:
        return int(path_parts[0])
    except (ValueError, TypeError):
        return None


def check_permission(current_user_id, path_parts, operation):
    """
    检查权限
    operation: 'read', 'write', 'delete'
    """
    # 访客模式：只能读取和下载
    if not current_user_id:
        if operation in ['write', 'delete']:
            return False, '访客没有上传或删除权限'
        return True, None
    
    # 根目录：只读
    if len(path_parts) == 0:
        if operation in ['write', 'delete']:
            return False, '根目录不允许上传或删除操作'
        return True, None
    
    # 获取路径所有者
    owner_id = get_path_owner_id(path_parts)
    
    # 自己的文件夹：完全权限
    if owner_id and owner_id == current_user_id:
        return True, None
    
    # 其他人的文件夹：只读
    if operation in ['write', 'delete']:
        return False, '没有权限修改其他用户的文件'
    
    return True, None


@csrf_exempt
@require_http_methods(["GET"])
def list_files(request):
    """
    获取文件列表
    支持路径参数指定子目录: ?path=user_id/subfolder
    首次访问时自动创建用户文件夹
    """
    try:
        # 可选地获取当前用户信息（如果已登录）
        current_user_id = getattr(request, 'user_id', None)
        current_username = getattr(request, 'username', None)
        
        # 获取请求的路径参数
        relative_path = request.GET.get('path', '').strip()
        path_parts = [p for p in relative_path.split('/') if p] if relative_path else []
        
        # 防止路径遍历攻击
        if '..' in relative_path or relative_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 确保根目录存在
        NETWORK_DISK_ROOT.mkdir(parents=True, exist_ok=True)
        
        # 如果用户已登录，确保用户文件夹存在
        if current_user_id:
            ensure_user_directory(current_user_id)
        
        # 构建完整路径（使用用户ID）
        if path_parts:
            # 如果第一个部分是用户ID，验证用户是否存在并确保目录存在
            try:
                first_part = path_parts[0]
                user_id = int(first_part)
                # 验证用户是否存在
                username = get_username_by_id(user_id)
                if not username:
                    return JsonResponse({
                        'success': False,
                        'error': '用户不存在'
                    }, status=404)
                # 确保用户目录存在
                ensure_user_directory(user_id)
            except (ValueError, TypeError):
                # 如果不是数字，可能是子目录，继续处理
                pass
            
            target_path = NETWORK_DISK_ROOT / '/'.join(path_parts)
        else:
            target_path = NETWORK_DISK_ROOT
        
        # 检查路径安全性
        if not check_path_safety(target_path, NETWORK_DISK_ROOT):
            return JsonResponse({
                'success': False,
                'error': '访问被拒绝'
            }, status=403)
        
        # 检查路径是否存在
        if not target_path.exists():
            return JsonResponse({
                'success': False,
                'error': '路径不存在'
            }, status=404)
        
        if not target_path.is_dir():
            # 如果是文件，返回 404，让前端尝试下载
            return JsonResponse({
                'success': False,
                'error': '路径是文件，不是目录'
            }, status=404)
        
        # 检查权限（读取权限）
        has_permission, error_msg = check_permission(current_user_id, path_parts, 'read')
        if not has_permission:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)
        
        # 获取文件列表
        files = []
        directories = []
        
        try:
            # 如果是根目录，只显示目录（用户文件夹）
            if len(path_parts) == 0:
                if target_path.exists():
                    for item in target_path.iterdir():
                        if item.is_dir():
                            # 尝试将目录名转换为用户ID，获取用户名
                            try:
                                user_id = int(item.name)
                                username = get_username_by_id(user_id)
                                if username:  # 只显示有效的用户目录
                                    file_info = get_file_info(item)
                                    # 使用用户名作为显示名称
                                    file_info['display_name'] = username
                                    file_info['user_id'] = user_id
                                    directories.append(file_info)
                            except (ValueError, TypeError):
                                # 如果不是数字，跳过
                                pass
            else:
                # 非根目录，正常显示所有文件和文件夹
                for item in target_path.iterdir():
                    file_info = get_file_info(item)
                    if file_info['is_directory']:
                        directories.append(file_info)
                    else:
                        files.append(file_info)
        except PermissionError:
            return JsonResponse({
                'success': False,
                'error': '没有权限访问该目录'
            }, status=403)
        
        # 排序：目录在前，按名称排序
        directories.sort(key=lambda x: (x.get('display_name') or x['name']).lower())
        files.sort(key=lambda x: x['name'].lower())
        
        # 检查当前路径的权限
        can_write, _ = check_permission(current_user_id, path_parts, 'write')
        can_delete, _ = check_permission(current_user_id, path_parts, 'delete')
        
        # 构建父路径
        parent_parts = path_parts[:-1] if path_parts else []
        parent_path = '/'.join(parent_parts) if parent_parts else ''
        
        # 获取路径中的用户名（用于显示）
        path_usernames = []
        for part in path_parts:
            try:
                user_id = int(part)
                username = get_username_by_id(user_id)
                path_usernames.append(username if username else part)
            except (ValueError, TypeError):
                path_usernames.append(part)
        
        # 获取当前路径的所有者用户ID和用户名
        current_owner_id = get_path_owner_id(path_parts)
        current_owner_username = None
        if current_owner_id:
            current_owner_username = get_username_by_id(current_owner_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_path': relative_path,
                'path_parts': path_parts,
                'path_usernames': path_usernames,  # 用于面包屑显示
                'current_user_id': current_user_id,
                'current_username': current_username,
                'current_owner_id': current_owner_id,  # 当前路径的所有者ID
                'current_owner_username': current_owner_username,  # 当前路径的所有者用户名
                'can_write': can_write,
                'can_delete': can_delete,
                'directories': directories,
                'files': files,
                'parent_path': parent_path
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文件列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def upload_file(request):
    """
    上传文件
    只能在用户自己的文件夹下上传（需要登录）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        current_username = getattr(request, 'username', None)
        
        if not current_user_id or not current_username:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        # 获取路径参数
        relative_path = request.POST.get('path', '').strip()
        path_parts = [p for p in relative_path.split('/') if p] if relative_path else []
        
        # 检查权限
        has_permission, error_msg = check_permission(current_user_id, path_parts, 'write')
        if not has_permission:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)
        
        # 检查是否有文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有上传文件'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 构建目标路径
        if path_parts:
            target_dir = NETWORK_DISK_ROOT / '/'.join(path_parts)
        else:
            # 根目录，使用当前用户的文件夹
            ensure_user_directory(current_user_id)
            target_dir = NETWORK_DISK_ROOT / str(current_user_id)
        
        # 确保目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查路径安全性
        if not check_path_safety(target_dir, NETWORK_DISK_ROOT):
            return JsonResponse({
                'success': False,
                'error': '访问被拒绝'
            }, status=403)
        
        # 保存文件
        file_path = target_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        file_info = get_file_info(file_path)
        
        return JsonResponse({
            'success': True,
            'message': '文件上传成功',
            'data': {
                'file': file_info
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def download_file(request, file_path):
    """
    下载文件
    所有用户都可以下载（包括访客）
    支持直接URL访问下载
    """
    try:
        # 防止路径遍历攻击
        if '..' in file_path or file_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 构建完整路径
        path_parts = [p for p in file_path.split('/') if p]
        target_file = NETWORK_DISK_ROOT / '/'.join(path_parts)
        
        # 检查路径安全性
        if not check_path_safety(target_file, NETWORK_DISK_ROOT):
            return JsonResponse({
                'success': False,
                'error': '访问被拒绝'
            }, status=403)
        
        # 检查文件是否存在
        if not target_file.exists() or not target_file.is_file():
            return JsonResponse({
                'success': False,
                'error': '文件不存在'
            }, status=404)
        
        # 返回文件
        response = FileResponse(
            open(target_file, 'rb'),
            as_attachment=True,
            filename=target_file.name
        )
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'文件下载失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["DELETE"])
def delete_file(request, file_path):
    """
    删除文件或目录
    只能删除自己文件夹下的文件（需要登录）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        # 防止路径遍历攻击
        if '..' in file_path or file_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 构建完整路径
        path_parts = [p for p in file_path.split('/') if p]
        target_path = NETWORK_DISK_ROOT / '/'.join(path_parts)
        
        # 检查路径安全性
        if not check_path_safety(target_path, NETWORK_DISK_ROOT):
            return JsonResponse({
                'success': False,
                'error': '访问被拒绝'
            }, status=403)
        
        # 检查权限
        has_permission, error_msg = check_permission(current_user_id, path_parts, 'delete')
        if not has_permission:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)
        
        # 检查路径是否存在
        if not target_path.exists():
            return JsonResponse({
                'success': False,
                'error': '文件或目录不存在'
            }, status=404)
        
        # 删除文件或目录
        import shutil
        if target_path.is_file():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)
        
        return JsonResponse({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def create_directory(request):
    """
    创建目录
    只能在自己的文件夹下创建（需要登录）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        current_username = getattr(request, 'username', None)
        
        if not current_user_id or not current_username:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        # 解析请求数据
        data = json.loads(request.body.decode())
        relative_path = data.get('path', '').strip()
        dir_name = data.get('name', '').strip()
        
        if not dir_name:
            return JsonResponse({
                'success': False,
                'error': '目录名不能为空'
            }, status=400)
        
        # 防止路径遍历攻击和非法字符
        if '..' in relative_path or relative_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        if '..' in dir_name or '/' in dir_name or '\\' in dir_name:
            return JsonResponse({
                'success': False,
                'error': '目录名包含非法字符'
            }, status=400)
        
        # 解析路径
        path_parts = [p for p in relative_path.split('/') if p] if relative_path else []
        
        # 检查权限
        has_permission, error_msg = check_permission(current_user_id, path_parts, 'write')
        if not has_permission:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)
        
        # 构建目标路径
        if path_parts:
            target_dir = NETWORK_DISK_ROOT / '/'.join(path_parts)
        else:
            # 根目录，使用当前用户的文件夹
            ensure_user_directory(current_user_id)
            target_dir = NETWORK_DISK_ROOT / str(current_user_id)
        
        # 确保路径在根目录内
        if not check_path_safety(target_dir, NETWORK_DISK_ROOT):
            return JsonResponse({
                'success': False,
                'error': '访问被拒绝'
            }, status=403)
        
        # 创建目录
        new_dir = target_dir / dir_name
        if new_dir.exists():
            return JsonResponse({
                'success': False,
                'error': '目录已存在'
            }, status=400)
        
        new_dir.mkdir(parents=True, exist_ok=True)
        
        return JsonResponse({
            'success': True,
            'message': '目录创建成功',
            'data': {
                'directory': {
                    'name': dir_name,
                    'path': '/'.join(path_parts + [dir_name]) if path_parts else dir_name
                }
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'创建目录失败: {str(e)}'
        }, status=500)
