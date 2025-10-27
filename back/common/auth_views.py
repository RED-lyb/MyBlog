import json
import traceback
from django.http import JsonResponse
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
        data = json.loads(request.body.decode())
        refresh_token = data.get('refresh_token', '').strip()

        # 基本验证
        if not refresh_token:
            return JsonResponse({
                'success': False,
                'error': '缺少刷新令牌',
                'code': 'MISSING_REFRESH_TOKEN'
            }, status=400)

        # 验证refresh token
        is_valid, payload, error_message = JWTUtils.verify_token(refresh_token)
        
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
        is_stored_valid, refresh_token_obj = RefreshTokenManager.verify_refresh_token(user_id, refresh_token)
        
        if not is_stored_valid:
            return JsonResponse({
                'success': False,
                'error': '刷新令牌无效或已过期',
                'code': 'REFRESH_TOKEN_INVALID'
            }, status=401)

        # 更新最后使用时间
        refresh_token_obj.update_last_used()

        # 生成新的access token
        new_access_token = JWTUtils.generate_access_token(user_id, username)

        return JsonResponse({
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

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的请求数据',
            'code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        print('[REFRESH_TOKEN] 未知异常:', traceback.format_exc())
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
        data = json.loads(request.body.decode())
        refresh_token = data.get('refresh_token', '').strip()

        if refresh_token:
            # 撤销refresh token
            RefreshTokenManager.revoke_refresh_token_by_token(refresh_token)

        return JsonResponse({
            'success': True,
            'message': '退出登录成功'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的请求数据',
            'code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        print('[LOGOUT] 未知异常:', traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': '退出登录异常，请稍后重试',
            'code': 'LOGOUT_ERROR'
        }, status=500)
