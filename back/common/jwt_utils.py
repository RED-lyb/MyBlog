import jwt
import datetime
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db import connection
import secrets
import hashlib
import threading
import time
from .captcha_utils import CaptchaUtils


def get_db_naive_time():
    """
    获取数据库服务器时间（naive datetime，无时区信息）
    与数据库存储的时间格式保持一致（与 users.registered_time 一致）
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT NOW()")
        db_now = cursor.fetchone()[0]
        # 确保返回的是 naive datetime（去掉时区信息）
        if hasattr(db_now, 'tzinfo') and db_now.tzinfo is not None:
            db_now = timezone.localtime(db_now).replace(tzinfo=None)
        return db_now


def ensure_naive_datetime(dt):
    """
    确保 datetime 是 naive（无时区信息）
    如果是有时区的 aware datetime，转换为 naive
    """
    if dt is None:
        return None
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return timezone.localtime(dt).replace(tzinfo=None)
    return dt


class JWTUtils:
    """
    JWT工具类
    实现短期Access Token + 长期Refresh Token机制
    """
    
    # JWT配置
    SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key')
    ALGORITHM = 'HS256'
    
    # Token过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Access Token 60分钟
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # Refresh Token 30天
    
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
        # 改为完全由数据库计算时间，避免Python与ORM时区转换造成的偏移
        lifetime_seconds = int(JWTUtils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO refresh_tokens (user_id, token_hash, expires_at, created_at)
                VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND), NOW())
                """,
                [user_id, token_hash, lifetime_seconds]
            )
    
    @classmethod
    def verify_refresh_token(cls, user_id, refresh_token):
        """
        验证Refresh Token
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # 完全用 SQL 校验并读取，直接用数据库时间判断过期，避免ORM时区歧义
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, token_hash, expires_at, created_at, last_used_at,
                       (expires_at > NOW()) AS is_valid
                FROM refresh_tokens
                WHERE user_id = %s AND token_hash = %s
                """,
                [user_id, token_hash]
            )
            row = cursor.fetchone()

        if not row:
            return False, None

        rec_id, rec_user_id, rec_hash, rec_expires_at, rec_created_at, rec_last_used_at, is_valid = row
        if not bool(is_valid):
            # 已过期：不在此处删除，交给后台清理任务；这里只返回无效
            return False, None

        # 构造一个轻量对象，附带 update_last_used 方法（使用 SQL 的 NOW()）
        class SimpleRefreshToken:
            def __init__(self, _id, _user_id, _expires_at, _created_at, _last_used_at):
                self.id = _id
                self.user_id = _user_id
                self.expires_at = _expires_at
                self.created_at = _created_at
                self.last_used_at = _last_used_at

            def update_last_used(self):
                with connection.cursor() as c:
                    c.execute(
                        "UPDATE refresh_tokens SET last_used_at = NOW() WHERE id = %s",
                        [self.id]
                    )

        return True, SimpleRefreshToken(
            rec_id, rec_user_id, rec_expires_at, rec_created_at, rec_last_used_at
        )
    
    @classmethod
    def revoke_refresh_token(cls, user_id):
        """
        撤销用户的Refresh Token
        返回删除的记录数
        """
        from .models import RefreshToken
        
        deleted_count, _ = RefreshToken.objects.filter(user_id=user_id).delete()
        return deleted_count
    
    @classmethod
    def revoke_refresh_token_by_token(cls, refresh_token):
        """
        通过token撤销Refresh Token
        返回删除的记录数
        """
        from .models import RefreshToken
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        deleted_count, _ = RefreshToken.objects.filter(token_hash=token_hash).delete()
        return deleted_count
    
    @classmethod
    def delete_refresh_token(cls, user_id, refresh_token):
        """
        删除指定用户的特定Refresh Token
        返回删除的记录数
        """
        from .models import RefreshToken
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        deleted_count, _ = RefreshToken.objects.filter(user_id=user_id, token_hash=token_hash).delete()
        return deleted_count
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """
        清理过期的Refresh Token
        使用本地时间进行比较
        """
        # 直接用数据库时间删除，避免ORM时区转换
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM refresh_tokens WHERE expires_at <= NOW()")


# 简单的后台清理任务：定期删除已过期的 refresh_tokens 和验证码
class _BackgroundCleaner:
    _started = False
    _interval_seconds = 60

    @classmethod
    def start(cls):
        if cls._started:
            return
        cls._started = True

        def _loop():
            while True:
                try:
                    RefreshTokenManager.cleanup_expired_tokens()
                except Exception:
                    pass
                try:
                    CaptchaUtils.cleanup_expired_captcha()
                except Exception:
                    pass
                time.sleep(cls._interval_seconds)

        t = threading.Thread(target=_loop, name="BackgroundCleanup", daemon=True)
        t.start()


# 在模块加载时启动后台清理任务
_BackgroundCleaner.start()


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
