"""
自定义中间件
"""
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .captcha_utils import LoginLimitUtils


class LoginLimitMiddleware(MiddlewareMixin):
    """
    登录限制中间件
    在请求处理前检查登录限制
    """
    
    def process_request(self, request):
        """
        处理请求前的逻辑
        """
        # 只对登录和找回密码相关的API进行限制检查
        if request.path in ['/api/login/', '/api/forgot/'] and request.method == 'POST':
            try:
                # 解析请求数据
                data = json.loads(request.body.decode())
                username = data.get('username', '')
                
                # 检查登录限制
                if LoginLimitUtils.is_locked(request, username):
                    # 返回限制响应
                    if request.path == '/api/login/':
                        response = JsonResponse({
                            'success': False,
                            'error': '尝试次数过多，账户已被锁定1小时',
                            'field_errors': {'non_field': '尝试次数过多，账户已被锁定1小时'}
                        }, status=429)
                    else:  # /api/forgot/
                        response = JsonResponse({
                            'status': 'false',
                            'message': '尝试次数过多，账户已被锁定1小时'
                        }, status=429)
                    return response
                    
            except (json.JSONDecodeError, Exception):
                # 如果解析失败，继续正常处理
                pass
        
        return None
    
    def process_response(self, request, response):
        """
        处理响应后的逻辑
        """
        return response
