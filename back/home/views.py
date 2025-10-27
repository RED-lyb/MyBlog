from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.db import connection


def home(request):
    """
    主页API
    返回用户信息或访客提示
    """
    # 检查用户是否已认证
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
                        'message': '欢迎回来',
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
                    
        except Exception as e:
            print(f"[HOME] 获取用户信息异常: {e}")
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
            'message': '欢迎访问',
            'data': {
                'user': None,
                'is_authenticated': False,
                'guest_message': '您当前以访客身份访问，请登录以获得完整功能'
            }
        })