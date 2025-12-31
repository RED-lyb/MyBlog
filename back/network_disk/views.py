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
import shutil
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


def calculate_directory_size(directory_path):
    """递归计算目录大小"""
    total_size = 0
    try:
        for item in directory_path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
    except (PermissionError, OSError):
        pass
    return total_size


def get_file_info(file_path):
    """获取文件信息"""
    stat = file_path.stat()
    size = stat.st_size
    size_formatted = format_file_size(size)
    
    # 如果是目录，计算目录大小
    if file_path.is_dir():
        dir_size = calculate_directory_size(file_path)
        size = dir_size
        size_formatted = format_file_size(dir_size)
    
    return {
        'name': file_path.name,
        'size': size,
        'size_formatted': size_formatted,
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
        
        # 获取筛选参数（仅在根目录时生效）
        filter_user_id = request.GET.get('filter_user_id', '').strip()
        filter_username = request.GET.get('filter_username', '').strip()
        only_mine = request.GET.get('only_mine', '').strip().lower() == 'true'
        
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
                                    # 应用筛选条件
                                    if only_mine and current_user_id:
                                        # 只看自己：只显示当前用户的目录
                                        if user_id != current_user_id:
                                            continue
                                    elif filter_user_id:
                                        # 按用户ID筛选（精确匹配）
                                        try:
                                            filter_id = int(filter_user_id)
                                            if user_id != filter_id:
                                                continue
                                        except (ValueError, TypeError):
                                            pass
                                    elif filter_username:
                                        # 按用户名筛选（模糊匹配）
                                        if filter_username.lower() not in username.lower():
                                            continue
                                    
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
        # 只有第一层（索引0）才映射成用户名，其他层直接显示文件夹名
        path_usernames = []
        for index, part in enumerate(path_parts):
            if index == 0:
                # 第一层：尝试映射成用户名
                try:
                    user_id = int(part)
                    username = get_username_by_id(user_id)
                    path_usernames.append(username if username else part)
                except (ValueError, TypeError):
                    path_usernames.append(part)
            else:
                # 其他层：直接使用文件夹名
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
        file_size = uploaded_file.size
        
        # 检查容量限制（在上传前检查）
        total_size_gb = 15.0  # 总容量15GB
        used_size_bytes = 0
        try:
            for item in NETWORK_DISK_ROOT.rglob('*'):
                if item.is_file():
                    used_size_bytes += item.stat().st_size
        except (PermissionError, OSError):
            pass
        
        # 计算上传后的使用量
        new_used_size_bytes = used_size_bytes + file_size
        new_used_size_gb = new_used_size_bytes / (1024 ** 3)
        
        # 如果超过100%，禁止上传
        if new_used_size_gb > total_size_gb:
            return JsonResponse({
                'success': False,
                'error': f'存储空间不足，无法上传。当前已用 {round(used_size_bytes / (1024 ** 3), 2)}G / {total_size_gb}G，上传此文件后将超过限制'
            }, status=400)
        
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
        
        # 上传后再次检查容量，如果超过100%则删除刚上传的文件
        try:
            new_used_size_bytes_check = 0
            for item in NETWORK_DISK_ROOT.rglob('*'):
                if item.is_file():
                    new_used_size_bytes_check += item.stat().st_size
            
            new_used_size_gb_check = new_used_size_bytes_check / (1024 ** 3)
            if new_used_size_gb_check > total_size_gb:
                # 删除刚上传的文件
                if file_path.exists():
                    file_path.unlink()
                return JsonResponse({
                    'success': False,
                    'error': '存储空间已满，文件已自动删除'
                }, status=400)
        except (PermissionError, OSError):
            # 如果检查失败，保留文件（避免误删）
            pass
        
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
    支持 Range 请求（用于检查文件是否存在而不下载）
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
        
        # 检查是否是 Range 请求（用于检查文件是否存在）
        range_header = request.META.get('HTTP_RANGE', '')
        if range_header and range_header.startswith('bytes=0-0'):
            # 只返回第一个字节，用于检查文件是否存在
            file_size = target_file.stat().st_size
            if file_size > 0:
                with open(target_file, 'rb') as f:
                    f.seek(0)
                    first_byte = f.read(1)
                    response = FileResponse(
                        first_byte,
                        status=206,  # Partial Content
                        content_type='application/octet-stream'
                    )
                    response['Content-Range'] = f'bytes 0-0/{file_size}'
                    response['Accept-Ranges'] = 'bytes'
                    return response
            else:
                # 空文件
                return FileResponse(
                    b'',
                    content_type='application/octet-stream'
                )
        
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


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def rename_item(request):
    """重命名文件或文件夹"""
    try:
        current_user_id = getattr(request, 'user_id', None)
        
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        # 解析请求数据
        data = json.loads(request.body.decode())
        relative_path = data.get('path', '').strip()
        new_name = data.get('new_name', '').strip()
        
        if not new_name:
            return JsonResponse({
                'success': False,
                'error': '新名称不能为空'
            }, status=400)
        
        # 防止路径遍历攻击和非法字符
        if '..' in relative_path or relative_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        if '..' in new_name or '/' in new_name or '\\' in new_name:
            return JsonResponse({
                'success': False,
                'error': '新名称包含非法字符'
            }, status=400)
        
        # 解析路径
        path_parts = [p for p in relative_path.split('/') if p] if relative_path else []
        
        # 构建目标路径（包含文件名/文件夹名）
        if path_parts:
            target_path = NETWORK_DISK_ROOT / '/'.join(path_parts)
        else:
            return JsonResponse({
                'success': False,
                'error': '根目录不能重命名'
            }, status=400)
        
        # 检查路径是否存在
        if not target_path.exists():
            return JsonResponse({
                'success': False,
                'error': '文件或目录不存在'
            }, status=404)
        
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
                'error': '文件或目录不存在'
            }, status=404)
        
        # 获取父路径部分（用于权限检查）
        parent_parts = path_parts[:-1] if len(path_parts) > 1 else path_parts[:1] if path_parts else []
        
        # 检查权限（基于父目录，如果是根目录下的用户文件夹，则使用path_parts[:1]）
        has_permission, error_msg = check_permission(current_user_id, parent_parts, 'write')
        if not has_permission:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=403)
        
        # 构建新路径
        parent_path = target_path.parent
        new_path = parent_path / new_name
        
        # 检查新名称是否已存在
        if new_path.exists():
            return JsonResponse({
                'success': False,
                'error': '新名称已存在'
            }, status=400)
        
        # 重命名
        target_path.rename(new_path)
        
        # 获取新文件信息
        file_info = get_file_info(new_path)
        
        return JsonResponse({
            'success': True,
            'message': '重命名成功',
            'data': {
                'item': file_info
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
            'error': f'重命名失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_storage_info(request):
    """获取存储信息（总容量15G，已使用，剩余）"""
    try:
        # 总容量：15GB
        total_size_gb = 15.0
        
        # 计算已使用空间
        used_size_bytes = 0
        try:
            for item in NETWORK_DISK_ROOT.rglob('*'):
                if item.is_file():
                    used_size_bytes += item.stat().st_size
        except (PermissionError, OSError):
            pass
        
        # 转换为GB
        used_size_gb = used_size_bytes / (1024 ** 3)
        remaining_size_gb = total_size_gb - used_size_gb
        
        # 精度为0.01G
        used_size_gb = round(used_size_gb, 2)
        remaining_size_gb = round(remaining_size_gb, 2)
        
        # 计算百分比
        usage_percentage = round((used_size_gb / total_size_gb) * 100, 2)
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_gb': total_size_gb,
                'used_gb': used_size_gb,
                'remaining_gb': remaining_size_gb,
                'usage_percentage': usage_percentage
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取存储信息失败: {str(e)}'
        }, status=500)
