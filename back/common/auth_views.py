import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from common.jwt_utils import JWTUtils, RefreshTokenManager


@csrf_exempt
def refresh_token(request):
    """
    刷新Access Token
    使用Refresh Token获取新的Access Token
    """
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)

    try:
        
        # 从HttpOnly Cookie中读取刷新令牌
        refresh_token_cookie = request.COOKIES.get('refresh_token', '').strip()

        if not refresh_token_cookie:
            return JsonResponse({
                'success': False,
                'error': '缺少刷新令牌',
                'code': 'MISSING_REFRESH_TOKEN'
            }, status=400)

        # 验证refresh token
        is_valid, payload, error_message = JWTUtils.verify_token(refresh_token_cookie)
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_message,
                'code': 'INVALID_REFRESH_TOKEN'
            }, status=401)

        # 检查token类型
        if payload.get('token_type') != 'refresh':
            return JsonResponse({
                'success': False,
                'error': '令牌类型错误',
                'code': 'INVALID_TOKEN_TYPE'
            }, status=401)

        user_id = payload.get('user_id')
        username = payload.get('username')

        # 验证refresh token是否在数据库中且有效
        is_stored_valid, refresh_token_obj = RefreshTokenManager.verify_refresh_token(user_id, refresh_token_cookie)
        
        if not is_stored_valid:
            return JsonResponse({
                'success': False,
                'error': '刷新令牌无效或已过期',
                'code': 'REFRESH_TOKEN_INVALID'
            }, status=401)

        # 检查 refresh_token 是否接近过期（少于总寿命的10%则轮换）
        
        # 使用数据库服务器时间进行比较（naive datetime）
        # 统一使用辅助函数获取数据库时间
        # 直接用数据库计算剩余秒数，避免任何时区换算偏移
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT TIMESTAMPDIFF(SECOND, NOW(), expires_at) FROM refresh_tokens WHERE id = %s",
                [refresh_token_obj.id]
            )
            row = cursor.fetchone()
            total_seconds = float(row[0]) if row and row[0] is not None else -1.0
        
        # 如果已过期，不应该到这里（应该在上一步验证时就被删除）
        if total_seconds <= 0:
            return JsonResponse({
                'success': False,
                'error': '刷新令牌已过期',
                'code': 'REFRESH_TOKEN_EXPIRED'
            }, status=401)
        
        # 不再进行 refresh_token 轮换：仅根据有效期决定是否允许刷新 access_token
        
        # 生成新的 access_token（总是生成新的）
        new_access_token = JWTUtils.generate_access_token(user_id, username)
        
        # 更新最后使用时间（数据库 NOW()）
        refresh_token_obj.update_last_used()
        
        # 始终只更新 access_token，refresh_token 不改变
        response = JsonResponse({
            'success': True,
            'message': '令牌刷新成功',
            'data': {
                'access_token': new_access_token,
                'user': {
                    'id': user_id,
                    'username': username
                }
            }
        })
        return response


    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的请求数据',
            'code': 'INVALID_JSON'
        }, status=400)
    except Exception:
        return JsonResponse({
            'success': False,
            'error': '令牌刷新异常，请稍后重试',
            'code': 'REFRESH_ERROR'
        }, status=500)


@csrf_exempt
def logout(request):
    """
    用户退出登录
    撤销Refresh Token
    """
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)

    try:
        # 从Cookie读取并撤销刷新令牌
        refresh_token_cookie = request.COOKIES.get('refresh_token', '').strip()

        if refresh_token_cookie:
            # 先尝试验证token获取user_id
            is_valid, payload, _ = JWTUtils.verify_token(refresh_token_cookie)
            
            if is_valid and payload.get('token_type') == 'refresh':
                user_id = payload.get('user_id')
                # 删除特定用户的特定token
                RefreshTokenManager.delete_refresh_token(user_id, refresh_token_cookie)
            else:
                # 如果token验证失败（可能已过期），尝试通过token_hash直接删除
                # 这样可以确保即使token过期也能清理数据库记录
                RefreshTokenManager.revoke_refresh_token_by_token(refresh_token_cookie)
        else:
            # 如果Cookie不存在，尝试从请求头获取access_token来获取user_id
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                is_valid, payload, _ = JWTUtils.verify_token(access_token)
                if is_valid and payload.get('token_type') == 'access':
                    user_id = payload.get('user_id')
                    RefreshTokenManager.revoke_refresh_token(user_id)

        response = JsonResponse({
            'success': True,
            'message': '退出登录成功'
        })

        # 删除Cookie（确保path匹配设置Cookie时的path）
        # 注意：delete_cookie 不支持 secure 和 samesite 参数
        # 设置 Cookie 时的 path 是 '/'，所以删除时也需要指定相同的 path
        response.delete_cookie('refresh_token', path='/')
        return response

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的请求数据',
            'code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '退出登录异常，请稍后重试',
            'code': 'LOGOUT_ERROR'
        }, status=500)
