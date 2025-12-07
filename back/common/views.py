from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection


@csrf_exempt
def get_user_info(request):
    """
    全局用户信息接口
    返回当前登录用户的详细信息，或访客状态
    适用于所有需要获取用户信息的场景
    """
    # 检查用户是否已认证（由 JWT 中间件设置）
    is_authenticated = getattr(request, 'is_authenticated', False)
    user_id = getattr(request, 'user_id', None)
    username = getattr(request, 'username', None)
    
    if is_authenticated and user_id and username:
        # 用户已登录，获取用户详细信息
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, protect, registered_time, avatar, bg_color, bg_pattern, corner_radius 
                    FROM users WHERE id = %s
                """, [user_id])
                row = cursor.fetchone()
                
                if row:
                    user_data = {
                        'id': row[0],
                        'username': row[1],
                        'protect': row[2],
                        'registered_time': row[3].isoformat() if row[3] else None,
                        'avatar': row[4],
                        'bg_color': row[5],
                        'bg_pattern': row[6],
                        'corner_radius': row[7]
                    }
                    
                    return JsonResponse({
                        'success': True,
                        'message': '获取用户信息成功',
                        'data': {
                            'user': user_data,
                            'is_authenticated': True
                        }
                    })
                else:
                    # 用户不存在
                    return JsonResponse({
                        'success': False,
                        'error': '用户信息不存在',
                        'data': {
                            'is_authenticated': False
                        }
                    }, status=404)
                    
        except Exception:
            return JsonResponse({
                'success': False,
                'error': '获取用户信息失败',
                'data': {
                    'is_authenticated': False
                }
            }, status=500)
    else:
        # 访客模式
            return JsonResponse({
                'success': True,
                'message': '访客模式',
                'data': {
                    'user': None,
                    'is_authenticated': False
                }
            })


@csrf_exempt
def get_user_by_id(request, user_id):
    """
    根据用户ID获取用户信息（公开接口，不需要认证）
    用于访问其他用户的主页
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, protect, registered_time, avatar, bg_color, bg_pattern, corner_radius 
                FROM users WHERE id = %s
            """, [user_id])
            row = cursor.fetchone()
            
            if row:
                user_data = {
                    'id': row[0],
                    'username': row[1],
                    'protect': row[2],
                    'registered_time': row[3].isoformat() if row[3] else None,
                    'avatar': row[4],
                    'bg_color': row[5],
                    'bg_pattern': row[6],
                    'corner_radius': row[7]
                }
                
                return JsonResponse({
                    'success': True,
                    'message': '获取用户信息成功',
                    'data': {
                        'user': user_data
                    }
                })
            else:
                # 用户不存在
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在',
                    'data': None
                }, status=404)
                
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取用户信息失败: {str(e)}',
            'data': None
        }, status=500)
