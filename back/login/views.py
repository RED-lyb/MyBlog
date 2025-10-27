import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.hashers import check_password
from common.captcha_utils import CaptchaUtils, captcha_required, LoginLimitUtils, login_limit_required
from common.jwt_utils import JWTUtils, RefreshTokenManager


@csrf_exempt
@login_limit_required
@captcha_required
def login(request):
    """
    用户登录
    """
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)

    try:
        data = json.loads(request.body.decode())
        username = data.get('username', '').strip()
        password = data.get('password', '')
        captcha_key = data.get('captcha_key', '')
        captcha_value = data.get('captcha_value', '')

        # 基本验证
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': '用户名和密码不能为空',
                'field_errors': {
                    'username': '请输入用户名' if not username else '',
                    'password': '请输入密码' if not password else ''
                }
            }, status=400)
        

        # 验证用户凭据
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE username=%s", [username])
            row = cursor.fetchone()

            if row:
                user_id, stored_password = row
                if check_password(password, stored_password):
                    # 登录成功，清除登录失败记录
                    LoginLimitUtils.clear_login_failure(request, username)
                    
                    # 生成JWT令牌
                    access_token = JWTUtils.generate_access_token(user_id, username)
                    refresh_token = JWTUtils.generate_refresh_token(user_id, username)
                    
                    # 存储refresh token到数据库
                    RefreshTokenManager.store_refresh_token(user_id, refresh_token)
                    
                    return JsonResponse({
                        'success': True,
                        'message': '登录成功',
                        'data': {
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'user': {
                                'id': user_id,
                                'username': username
                            }
                        }
                    })
                else:
                    # 密码错误，记录失败次数
                    fail_count = LoginLimitUtils.record_login_failure(request, username)
                    remaining = 5 - fail_count
                    
                    if remaining <= 0:
                        return JsonResponse({
                            'success': False,
                            'error': '密码错误次数过多，账户已被锁定1小时',
                            'field_errors': {'non_field': '密码错误次数过多，账户已被锁定1小时'}
                        }, status=429)
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': f'密码错误，还有{remaining}次机会',
                            'field_errors': {'password': f'密码错误，还有{remaining}次机会'}
                        }, status=400)
            else:
                # 用户不存在，也记录失败次数
                fail_count = LoginLimitUtils.record_login_failure(request, username)
                remaining = 5 - fail_count
                
                if remaining <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': '用户不存在，尝试次数过多，账户已被锁定1小时',
                        'field_errors': {'non_field': '用户不存在，尝试次数过多，账户已被锁定1小时'}
                    }, status=429)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'用户不存在，还有{remaining}次机会',
                        'field_errors': {'username': f'用户不存在，还有{remaining}次机会'}
                    }, status=400)

    except Exception as e:
        print('[LOGIN] 未知异常:', traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': '登录异常，请稍后重试',
            'field_errors': {'non_field': '登录异常，请稍后重试'}
        }, status=500)