import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from common.jwt_utils import JWTUtils


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    JWT认证中间件
    自动为请求添加用户信息
    """
    
    def process_request(self, request):
        """
        处理请求，添加用户信息
        """
        # 不需要认证的路径
        public_paths = [
            '/api/login/',
            '/api/register/',
            '/api/forgot/',
            '/api/captcha/',
            '/api/auth/refresh/',
            '/api/auth/logout/',
        ]
        
        # 如果是公开路径，跳过认证
        if request.path in public_paths:
            return None
        
        # 从请求头获取Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            # 没有token，设置为访客
            request.user_id = None
            request.username = None
            request.is_authenticated = False
            return None
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        is_valid, payload, error_message = JWTUtils.verify_token(token)
        
        if not is_valid:
            # token无效，设置为访客
            request.user_id = None
            request.username = None
            request.is_authenticated = False
            return None
        
        # 检查token类型
        if payload.get('token_type') != 'access':
            # token类型错误，设置为访客
            request.user_id = None
            request.username = None
            request.is_authenticated = False
            return None
        
        # 设置用户信息
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        request.is_authenticated = True
        
        return None


class JWTAuthRequiredMiddleware(MiddlewareMixin):
    """
    JWT强制认证中间件
    用于需要强制认证的API
    """
    
    def process_request(self, request):
        """
        处理请求，强制要求认证
        """
        # 需要强制认证的路径
        protected_paths = [
            '/api/user/profile/',
            '/api/user/settings/',
            '/api/user/avatar/',
        ]
        
        # 如果不是受保护路径，跳过
        if request.path not in protected_paths:
            return None
        
        # 检查是否已认证
        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': '需要登录才能访问此资源',
                'code': 'AUTHENTICATION_REQUIRED'
            }, status=401)
        
        return None
