# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
import datetime


class Users(models.Model):
    username = models.CharField(unique=True, max_length=50, db_comment='登录名，全局唯一')
    password = models.CharField(max_length=255, db_comment='加密后的登录密码')
    protect = models.CharField(max_length=255, db_comment='密保问题原文')
    answer = models.CharField(max_length=255, db_comment='密保答案')
    registered_time = models.DateTimeField(db_comment='注册时间，默认当前时间')
    avatar = models.CharField(max_length=500, blank=True, null=True, db_comment='头像 URL，空表示未上传')
    bg_color = models.CharField(max_length=20, blank=True, null=True, db_comment='个人中心背景色，CSS 合法值')
    bg_pattern = models.CharField(max_length=50, blank=True, null=True, db_comment='背景点缀样式名或 URL')
    corner_radius = models.CharField(max_length=10, blank=True, null=True, db_comment='卡片圆角大小，单位 px 或百分比')

    class Meta:
        managed = False
        db_table = 'users'


class RefreshToken(models.Model):
    """
    Refresh Token模型
    用于存储用户的刷新令牌
    使用数据库服务器时间（与 users 表的 registered_time 保持一致）
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(db_comment='用户ID')
    token_hash = models.CharField(max_length=64, db_comment='Refresh Token的哈希值')
    expires_at = models.DateTimeField(db_comment='过期时间')
    # 使用数据库的 CURRENT_TIMESTAMP，与 users.registered_time 保持一致
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    last_used_at = models.DateTimeField(null=True, blank=True, db_comment='最后使用时间')
    
    class Meta:
        managed = True
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"RefreshToken for user {self.user_id}"
    
    def is_expired(self):
        """
        检查token是否过期
        使用数据库服务器时间进行比较（与 users.registered_time 保持一致）
        """
        from common.jwt_utils import get_db_naive_time, ensure_naive_datetime
        db_now = get_db_naive_time()
        expires_at = ensure_naive_datetime(self.expires_at)
        return db_now > expires_at
    
    def update_last_used(self):
        """
        更新最后使用时间
        使用数据库服务器时间（CURRENT_TIMESTAMP），与 users.registered_time 保持一致
        """
        from django.db import connection
        with connection.cursor() as cursor:
            # 使用数据库的 NOW() 函数获取服务器时间
            cursor.execute(
                "UPDATE refresh_tokens SET last_used_at = NOW() WHERE id = %s",
                [self.id]
            )


class BlogArticle(models.Model):
    """
    博客文章模型
    使用 managed = False，由 SQL 直接管理表结构
    """
    id = models.AutoField(primary_key=True, db_comment='文章ID，主键自增')
    title = models.CharField(max_length=500, db_comment='文章标题')
    content = models.TextField(db_comment='文章正文，支持 Markdown/HTML')
    author_id = models.IntegerField(db_comment='作者ID，外键关联 users 表')
    view_count = models.IntegerField(default=0, db_comment='浏览量，默认0')
    love_count = models.IntegerField(default=0, db_comment='点赞数，默认0')
    comment_count = models.IntegerField(default=0, db_comment='评论数，默认0，冗余字段便于查询')
    published_at = models.DateTimeField(db_comment='发布时间，默认服务器系统时间')
    
    class Meta:
        managed = False
        db_table = 'blog_articles'