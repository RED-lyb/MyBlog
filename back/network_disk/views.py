"""
网盘文件管理视图
提供文件列表、上传、下载、删除等功能
"""
import os
import json
from pathlib import Path
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from common.jwt_utils import jwt_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# 网盘文件根目录
NETWORK_DISK_ROOT = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'


def get_user_files_dir(user_id):
    """获取用户的文件目录"""
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


@csrf_exempt
@jwt_required
@require_http_methods(["GET"])
def list_files(request):
    """
    获取文件列表
    支持路径参数指定子目录: ?path=subfolder
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 获取请求的路径参数
        relative_path = request.GET.get('path', '').strip()
        if relative_path:
            # 防止路径遍历攻击
            if '..' in relative_path or relative_path.startswith('/'):
                return JsonResponse({
                    'success': False,
                    'error': '无效的路径'
                }, status=400)
        
        # 构建完整路径
        user_dir = get_user_files_dir(user_id)
        target_path = user_dir / relative_path if relative_path else user_dir
        
        # 确保路径在用户目录内
        try:
            target_path = target_path.resolve()
            user_dir_resolved = user_dir.resolve()
            if not str(target_path).startswith(str(user_dir_resolved)):
                return JsonResponse({
                    'success': False,
                    'error': '访问被拒绝'
                }, status=403)
        except (OSError, ValueError):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 检查路径是否存在
        if not target_path.exists():
            return JsonResponse({
                'success': False,
                'error': '路径不存在'
            }, status=404)
        
        if not target_path.is_dir():
            return JsonResponse({
                'success': False,
                'error': '不是目录'
            }, status=400)
        
        # 获取文件列表
        files = []
        directories = []
        
        try:
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
        directories.sort(key=lambda x: x['name'].lower())
        files.sort(key=lambda x: x['name'].lower())
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_path': relative_path,
                'directories': directories,
                'files': files,
                'parent_path': os.path.dirname(relative_path) if relative_path else ''
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
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 获取路径参数
        relative_path = request.POST.get('path', '').strip()
        
        # 检查是否有文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有上传文件'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 构建目标路径
        user_dir = get_user_files_dir(user_id)
        if relative_path:
            if '..' in relative_path or relative_path.startswith('/'):
                return JsonResponse({
                    'success': False,
                    'error': '无效的路径'
                }, status=400)
            target_dir = user_dir / relative_path
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = user_dir
        
        # 确保路径在用户目录内
        try:
            target_dir_resolved = target_dir.resolve()
            user_dir_resolved = user_dir.resolve()
            if not str(target_dir_resolved).startswith(str(user_dir_resolved)):
                return JsonResponse({
                    'success': False,
                    'error': '访问被拒绝'
                }, status=403)
        except (OSError, ValueError):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
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
@jwt_required
@require_http_methods(["GET"])
def download_file(request, file_path):
    """
    下载文件
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 防止路径遍历攻击
        if '..' in file_path or file_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 构建完整路径
        user_dir = get_user_files_dir(user_id)
        target_file = user_dir / file_path
        
        # 确保路径在用户目录内
        try:
            target_file_resolved = target_file.resolve()
            user_dir_resolved = user_dir.resolve()
            if not str(target_file_resolved).startswith(str(user_dir_resolved)):
                return JsonResponse({
                    'success': False,
                    'error': '访问被拒绝'
                }, status=403)
        except (OSError, ValueError):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
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
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 防止路径遍历攻击
        if '..' in file_path or file_path.startswith('/'):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
        # 构建完整路径
        user_dir = get_user_files_dir(user_id)
        target_path = user_dir / file_path
        
        # 确保路径在用户目录内
        try:
            target_path_resolved = target_path.resolve()
            user_dir_resolved = user_dir.resolve()
            if not str(target_path_resolved).startswith(str(user_dir_resolved)):
                return JsonResponse({
                    'success': False,
                    'error': '访问被拒绝'
                }, status=403)
        except (OSError, ValueError):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
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
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
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
        
        # 构建目标路径
        user_dir = get_user_files_dir(user_id)
        if relative_path:
            target_dir = user_dir / relative_path
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = user_dir
        
        # 确保路径在用户目录内
        try:
            target_dir_resolved = target_dir.resolve()
            user_dir_resolved = user_dir.resolve()
            if not str(target_dir_resolved).startswith(str(user_dir_resolved)):
                return JsonResponse({
                    'success': False,
                    'error': '访问被拒绝'
                }, status=403)
        except (OSError, ValueError):
            return JsonResponse({
                'success': False,
                'error': '无效的路径'
            }, status=400)
        
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
                    'path': str(new_dir.relative_to(user_dir))
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
