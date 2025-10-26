"""
验证码工具类
提供验证码生成、验证和登录限制功能
"""
import json
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import hashlib


class CaptchaUtils:
    """验证码工具类"""
    
    @staticmethod
    def generate_captcha(request=None):
        """
        生成验证码
        返回验证码的key和图片URL
        """
        try:
            # 生成新的验证码
            captcha_key = CaptchaStore.generate_key()
            captcha_image = captcha_image_url(captcha_key)
            
            # 如果是相对路径，需要转换为完整URL
            if captcha_image.startswith('/'):
                if request:
                    # 使用请求的host信息构建完整URL
                    scheme = 'https' if request.is_secure() else 'http'
                    host = request.get_host()
                    captcha_image = f"{scheme}://{host}{captcha_image}"
                else:
                    # 如果没有request对象，使用默认配置
                    captcha_image = f"http://localhost:8000{captcha_image}"
            
            return {
                'success': True,
                'captcha_key': captcha_key,
                'captcha_image': captcha_image
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'生成验证码失败: {str(e)}'
            }
    
    @staticmethod
    def verify_captcha(captcha_key, captcha_value):
        """
        验证验证码
        """
        try:
            if not captcha_key or not captcha_value:
                return False, '验证码不能为空'
            
            # 使用Django Simple Captcha的验证方法
            captcha_obj = CaptchaStore.objects.get(hashkey=captcha_key)
            
            if captcha_obj.expiration < timezone.now():
                return False, '验证码已过期'
            
            if captcha_obj.response.lower() == captcha_value.lower():
                # 验证成功后删除验证码
                captcha_obj.delete()
                return True, '验证成功'
            else:
                return False, '验证码错误'
                
        except CaptchaStore.DoesNotExist:
            return False, '验证码不存在或已过期'
        except Exception as e:
            return False, f'验证码验证失败: {str(e)}'


class LoginLimitUtils:
    """登录限制工具类"""
    
    @staticmethod
    def get_client_ip(request):
        """
        获取客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_identifier(request, username=None):
        """
        获取用户标识符，优先使用用户名，其次使用IP
        """
        if username:
            return f"user_{username}"
        else:
            ip = LoginLimitUtils.get_client_ip(request)
            return f"ip_{ip}"
    
    @staticmethod
    def check_login_limit(request, username=None):
        """
        检查登录限制
        返回 (is_allowed, error_message, remaining_attempts)
        """
        identifier = LoginLimitUtils.get_user_identifier(request, username)
        
        # 检查是否被锁定
        lock_key = f"login_lock_{identifier}"
        if cache.get(lock_key):
            return False, "账户已被锁定，请1小时后再试", 0
        
        # 检查失败次数
        fail_key = f"login_fail_{identifier}"
        fail_count = cache.get(fail_key, 0)
        
        if fail_count >= 5:
            # 锁定1小时
            cache.set(lock_key, True, 3600)  # 3600秒 = 1小时
            cache.delete(fail_key)  # 清除失败计数
            return False, "登录失败次数过多，账户已被锁定1小时", 0
        
        remaining = 5 - fail_count
        return True, "", remaining
    
    @staticmethod
    def record_login_failure(request, username=None):
        """
        记录登录失败
        """
        identifier = LoginLimitUtils.get_user_identifier(request, username)
        fail_key = f"login_fail_{identifier}"
        
        # 获取当前失败次数
        fail_count = cache.get(fail_key, 0)
        fail_count += 1
        
        # 设置失败次数，过期时间为1小时
        cache.set(fail_key, fail_count, 3600)
        
        return fail_count
    
    @staticmethod
    def is_locked(request, username=None):
        """
        检查是否被锁定
        """
        identifier = LoginLimitUtils.get_user_identifier(request, username)
        fail_key = f"login_fail_{identifier}"
        fail_count = cache.get(fail_key, 0)
        return fail_count >= 5
    
    @staticmethod
    def clear_login_failure(request, username=None):
        """
        清除登录失败记录
        """
        identifier = LoginLimitUtils.get_user_identifier(request, username)
        fail_key = f"login_fail_{identifier}"
        cache.delete(fail_key)


def captcha_required(view_func):
    """
    验证码装饰器
    用于需要验证码的视图函数
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode())
                captcha_key = data.get('captcha_key', '')
                captcha_value = data.get('captcha_value', '')
                
                is_valid, message = CaptchaUtils.verify_captcha(captcha_key, captcha_value)
                if not is_valid:
                    return JsonResponse({
                        'success': False,
                        'error': message,
                        'field_errors': {'captcha': message}
                    })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': '验证码验证失败',
                    'field_errors': {'captcha': '验证码验证失败'}
                }, status=400)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def login_limit_required(view_func):
    """
    登录限制装饰器
    用于需要登录限制的视图函数
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode())
                username = data.get('username', '')
                
                is_allowed, error_message, remaining = LoginLimitUtils.check_login_limit(request, username)
                if not is_allowed:
                    return JsonResponse({
                        'success': False,
                        'error': error_message,
                        'field_errors': {'non_field': error_message}
                    }, status=429)  # Too Many Requests
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': '登录限制检查失败',
                    'field_errors': {'non_field': '登录限制检查失败'}
                }, status=500)
        
        return view_func(request, *args, **kwargs)
    return wrapper
