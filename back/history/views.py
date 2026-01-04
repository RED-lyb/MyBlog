"""
更新历史相关视图
"""
import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from common.jwt_utils import jwt_required
from functools import wraps


def admin_required(view_func):
    """
    管理员权限装饰器
    需要先通过JWT认证，然后检查用户是否为管理员
    """
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        # jwt_required 已经设置了 request.user_id
        user_id = request.user_id
        
        # 检查用户是否为管理员
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", [user_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                return JsonResponse({
                    'success': False,
                    'error': '需要管理员权限',
                    'code': 'ADMIN_REQUIRED'
                }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


@csrf_exempt
@require_GET
def get_update_history_list(request):
    """
    获取更新历史列表（公开接口）
    按更新日期倒序排列（最新的在最上面）
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, update_time, update_content 
                FROM update_history 
                ORDER BY update_time DESC
            """)
            rows = cursor.fetchall()
            
            history_list = []
            for row in rows:
                history_list.append({
                    'id': row[0],
                    'update_time': row[1].isoformat() if row[1] else None,
                    'update_content': row[2]
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'history': history_list
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取更新历史失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_GET
def admin_get_update_history_list(request):
    """
    获取更新历史列表（管理员）
    """
    return get_update_history_list(request)


@csrf_exempt
@admin_required
@require_GET
def admin_get_update_history(request, history_id):
    """
    获取单条更新历史详情（管理员）
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, update_time, update_content 
                FROM update_history 
                WHERE id = %s
            """, [history_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '更新历史不存在'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'update_time': row[1].isoformat() if row[1] else None,
                    'update_content': row[2]
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取更新历史失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_POST
def admin_create_update_history(request):
    """
    创建更新历史（管理员）
    """
    try:
        data = json.loads(request.body.decode())
        update_content = data.get('update_content', '').strip()
        
        if not update_content:
            return JsonResponse({
                'success': False,
                'error': '更新内容不能为空'
            }, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO update_history (update_content) 
                VALUES (%s)
            """, [update_content])
            
            history_id = cursor.lastrowid
            
            # 获取创建后的记录
            cursor.execute("""
                SELECT id, update_time, update_content 
                FROM update_history 
                WHERE id = %s
            """, [history_id])
            row = cursor.fetchone()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'update_time': row[1].isoformat() if row[1] else None,
                    'update_content': row[2]
                },
                'message': '更新历史创建成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'创建更新历史失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["PUT"])
def admin_update_update_history(request, history_id):
    """
    更新更新历史（管理员）
    """
    try:
        data = json.loads(request.body.decode())
        update_content = data.get('update_content', '').strip()
        
        if not update_content:
            return JsonResponse({
                'success': False,
                'error': '更新内容不能为空'
            }, status=400)
        
        with connection.cursor() as cursor:
            # 检查记录是否存在
            cursor.execute("SELECT id FROM update_history WHERE id = %s", [history_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '更新历史不存在'
                }, status=404)
            
            # 更新记录
            cursor.execute("""
                UPDATE update_history 
                SET update_content = %s 
                WHERE id = %s
            """, [update_content, history_id])
            
            # 获取更新后的记录
            cursor.execute("""
                SELECT id, update_time, update_content 
                FROM update_history 
                WHERE id = %s
            """, [history_id])
            row = cursor.fetchone()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'update_time': row[1].isoformat() if row[1] else None,
                    'update_content': row[2]
                },
                'message': '更新历史更新成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新更新历史失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["DELETE"])
def admin_delete_update_history(request, history_id):
    """
    删除更新历史（管理员）
    """
    try:
        with connection.cursor() as cursor:
            # 检查记录是否存在
            cursor.execute("SELECT id FROM update_history WHERE id = %s", [history_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '更新历史不存在'
                }, status=404)
            
            # 删除记录
            cursor.execute("DELETE FROM update_history WHERE id = %s", [history_id])
            
            return JsonResponse({
                'success': True,
                'message': '更新历史删除成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除更新历史失败: {str(e)}'
        }, status=500)
