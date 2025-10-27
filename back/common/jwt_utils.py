import jwt
import datetime
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
import secrets
import hashlib


class JWTUtils:
    """
    JWT工具类
    实现短期Access Token + 长期Refresh Token机制
    """
    
    # JWT配置
    SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key')
    ALGORITHM = 'HS256'
    
    # Token过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access Token 30分钟
    REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh Token 7天
    
    @classmethod
    def generate_access_token(cls, user_id, username):
        """
        生成Access Token
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'token_type': 'access',
            'exp': timezone.now() + datetime.timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': timezone.now(),
            'jti': secrets.token_urlsafe(32)  # JWT ID，用于唯一标识
        }
        
        token = jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token
    
    @classmethod
    def generate_refresh_token(cls, user_id, username):
        """
        生成Refresh Token
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'token_type': 'refresh',
            'exp': timezone.now() + datetime.timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': timezone.now(),
            'jti': secrets.token_urlsafe(32)  # JWT ID，用于唯一标识
        }
        
        token = jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token
    
    @classmethod
    def verify_token(cls, token):
        """
        验证Token
        返回 (is_valid, payload, error_message)
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return True, payload, None
        except jwt.ExpiredSignatureError:
            return False, None, "Token已过期"
        except jwt.InvalidTokenError:
            return False, None, "Token无效"
        except Exception as e:
            return False, None, f"Token验证失败: {str(e)}"
    
    @classmethod
    def get_token_payload(cls, token):
        """
        获取Token载荷（不验证过期时间）
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM], options={"verify_exp": False})
            return payload
        except jwt.InvalidTokenError:
            return None
    
    @classmethod
    def is_token_expired(cls, token):
        """
        检查Token是否过期
        """
        try:
            jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return False  # 未过期
        except jwt.ExpiredSignatureError:
            return True   # 已过期
        except:
            return True   # 其他错误视为过期


class RefreshTokenManager:
    """
    Refresh Token管理器
    负责管理Refresh Token的存储、验证和清理
    """
    
    @classmethod
    def store_refresh_token(cls, user_id, refresh_token):
        """
        存储Refresh Token到数据库
        """
        from .models import RefreshToken
        
        # 生成token的hash值用于存储
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # 删除该用户之前的refresh token
        RefreshToken.objects.filter(user_id=user_id).delete()
        
        # 创建新的refresh token记录
        RefreshToken.objects.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=timezone.now() + datetime.timedelta(days=JWTUtils.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    
    @classmethod
    def verify_refresh_token(cls, user_id, refresh_token):
        """
        验证Refresh Token
        """
        from .models import RefreshToken
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        try:
            refresh_token_obj = RefreshToken.objects.get(
                user_id=user_id,
                token_hash=token_hash,
                expires_at__gt=timezone.now()
            )
            return True, refresh_token_obj
        except RefreshToken.DoesNotExist:
            return False, None
    
    @classmethod
    def revoke_refresh_token(cls, user_id):
        """
        撤销用户的Refresh Token
        """
        from .models import RefreshToken
        
        RefreshToken.objects.filter(user_id=user_id).delete()
    
    @classmethod
    def revoke_refresh_token_by_token(cls, refresh_token):
        """
        通过token撤销Refresh Token
        """
        from .models import RefreshToken
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        RefreshToken.objects.filter(token_hash=token_hash).delete()
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """
        清理过期的Refresh Token
        """
        from .models import RefreshToken
        
        RefreshToken.objects.filter(expires_at__lte=timezone.now()).delete()


def jwt_required(view_func):
    """
    JWT认证装饰器
    用于需要JWT认证的视图函数
    """
    from functools import wraps
    from django.http import JsonResponse
    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 从请求头获取Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'error': '缺少认证令牌',
                'code': 'MISSING_TOKEN'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        is_valid, payload, error_message = JWTUtils.verify_token(token)
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_message,
                'code': 'INVALID_TOKEN'
            }, status=401)
        
        # 检查token类型
        if payload.get('token_type') != 'access':
            return JsonResponse({
                'success': False,
                'error': '令牌类型错误',
                'code': 'INVALID_TOKEN_TYPE'
            }, status=401)
        
        # 将用户信息添加到request中
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
