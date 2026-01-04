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
    """
    用户表
    存储用户的基本信息和统计数据
    """
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    username = models.CharField(unique=True, max_length=50, db_comment='登录名，全局唯一')
    password = models.CharField(max_length=255, db_comment='加密后的登录密码')
    protect = models.CharField(max_length=255, db_comment='密保问题原文')
    answer = models.CharField(max_length=255, db_comment='密保答案')
    registered_time = models.DateTimeField(auto_now_add=True, db_comment='注册时间，默认当前时间')
    avatar = models.CharField(max_length=500, blank=True, null=True, db_comment='头像 URL，空表示未上传')
    bg_color = models.CharField(max_length=20, blank=True, null=True, db_comment='个人中心背景色，CSS 合法值')
    bg_pattern = models.CharField(max_length=50, blank=True, null=True, db_comment='背景点缀样式')
    corner_radius = models.CharField(max_length=10, blank=True, null=True, db_comment='卡片圆角大小，单位 px 或百分比')
    follow_count = models.PositiveIntegerField(default=0, db_comment='关注数，默认0')
    article_count = models.PositiveIntegerField(default=0, db_comment='发布文章数，默认0')
    liked_article_count = models.PositiveIntegerField(default=0, db_comment='喜欢的文章数，默认0')
    follower_count = models.PositiveIntegerField(default=0, db_comment='粉丝数，默认0')
    is_admin = models.BooleanField(default=False, db_comment='是否为管理员，0-否，1-是')

    class Meta:
        managed = False
        db_table = 'users'
    
    def __str__(self):
        return f"User {self.username} (ID: {self.id})"


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
    # 使用数据库的 CURRENT_TIMESTAMP(6)，与 SQL 表结构保持一致
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    last_used_at = models.DateTimeField(null=True, blank=True, db_comment='最后使用时间')
    
    class Meta:
        managed = False
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['user_id'], name='refresh_tok_user_id_46676d_idx'),
            models.Index(fields=['token_hash'], name='refresh_tok_token_h_2fa7c6_idx'),
            models.Index(fields=['expires_at'], name='refresh_tok_expires_a128d9_idx'),
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
    author_id = models.PositiveIntegerField(db_comment='作者ID，外键关联 users 表')
    view_count = models.PositiveIntegerField(default=0, db_comment='浏览量，默认0')
    love_count = models.PositiveIntegerField(default=0, db_comment='喜欢数，默认0')
    comment_count = models.PositiveIntegerField(default=0, db_comment='评论数，默认0，冗余字段便于查询')
    published_at = models.DateTimeField(auto_now_add=True, db_comment='发布时间，默认服务器系统时间')
    
    class Meta:
        managed = False
        db_table = 'blog_articles'
        indexes = [
            models.Index(fields=['author_id'], name='idx_author_id'),
            models.Index(fields=['published_at'], name='idx_published_at'),
            models.Index(fields=['view_count'], name='idx_view_count'),
        ]
    
    def __str__(self):
        return f"Article {self.id}: {self.title[:50]}"


class UserFollow(models.Model):
    """
    用户关注关系表
    记录用户之间的关注关系
    """
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    follower_id = models.PositiveIntegerField(db_comment='关注者ID，外键关联 users 表')
    following_id = models.PositiveIntegerField(db_comment='被关注者ID，外键关联 users 表')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='关注时间，默认服务器系统时间')
    
    class Meta:
        managed = False
        db_table = 'user_follows'
        unique_together = [['follower_id', 'following_id']]  # 防止重复关注
        indexes = [
            models.Index(fields=['follower_id'], name='idx_follower'),  # 查询某用户关注了哪些人
            models.Index(fields=['following_id'], name='idx_following'),  # 查询某用户被哪些人关注
        ]
    
    def __str__(self):
        return f"User {self.follower_id} follows User {self.following_id}"


class UserLikedArticle(models.Model):
    """
    用户喜欢的文章关系表
    记录用户对文章的喜欢关系
    """
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    user_id = models.PositiveIntegerField(db_comment='用户ID，外键关联 users 表')
    article_id = models.PositiveIntegerField(db_comment='文章ID，外键关联 blog_articles 表')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='喜欢时间，默认服务器系统时间')
    
    class Meta:
        managed = False
        db_table = 'user_liked_articles'
        unique_together = [['user_id', 'article_id']]  # 防止重复喜欢
        indexes = [
            models.Index(fields=['user_id'], name='idx_user'),  # 查询某用户喜欢了哪些文章
            models.Index(fields=['article_id'], name='idx_article'),  # 查询某文章被哪些用户喜欢
        ]
    
    def __str__(self):
        return f"User {self.user_id} liked Article {self.article_id}"


class ArticleComment(models.Model):
    """
    文章评论表
    记录用户对文章的评论
    """
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    article_id = models.PositiveIntegerField(db_comment='文章ID，外键关联 blog_articles 表')
    user_id = models.PositiveIntegerField(db_comment='评论用户ID，外键关联 users 表')
    content = models.CharField(max_length=200, db_comment='评论内容，最多200字')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='评论时间，默认服务器系统时间')
    
    class Meta:
        managed = False
        db_table = 'article_comments'
        indexes = [
            models.Index(fields=['article_id'], name='idx_article_id'),  # 查询某文章的所有评论
            models.Index(fields=['user_id'], name='idx_article_comment_user_id'),  # 查询某用户的所有评论
            models.Index(fields=['created_at'], name='idx_article_comment_created_at'),  # 按时间排序
        ]
    
    def __str__(self):
        return f"Comment {self.id} on Article {self.article_id} by User {self.user_id}"


class Feedback(models.Model):
    """
    反馈意见表
    记录用户或访客的反馈意见
    """
    ISSUE_TYPE_CHOICES = [
        ('使用错误', '使用错误'),
        ('功能建议', '功能建议'),
    ]
    
    RESOLVED_STATUS_CHOICES = [
        ('未解决', '未解决'),
        ('已解决', '已解决'),
        ('未采纳', '未采纳'),
    ]
    
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    user_id = models.PositiveIntegerField(null=True, blank=True, db_comment='提出用户ID，外键关联 users 表，NULL表示匿名反馈')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, db_comment='问题类型：使用错误、功能建议')
    description = models.TextField(db_comment='问题描述')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='问题提出时间，默认服务器系统时间')
    is_resolved = models.CharField(max_length=10, choices=RESOLVED_STATUS_CHOICES, default='未解决', db_comment='解决状态：未解决、已解决、未采纳')
    resolved_at = models.DateTimeField(null=True, blank=True, db_comment='解决时间，未解决时为NULL')
    
    class Meta:
        managed = False
        db_table = 'feedbacks'
        indexes = [
            models.Index(fields=['user_id'], name='idx_feedback_user_id'),  # 查询某用户的反馈
            models.Index(fields=['issue_type'], name='idx_issue_type'),  # 按问题类型查询
            models.Index(fields=['is_resolved'], name='idx_is_resolved'),  # 查询已解决/未解决的反馈
            models.Index(fields=['created_at'], name='idx_feedback_created_at'),  # 按时间排序
        ]
    
    def __str__(self):
        user_info = f"User {self.user_id}" if self.user_id else "Anonymous"
        return f"Feedback {self.id} by {user_info} - {self.issue_type}"


class UpdateHistory(models.Model):
    """
    更新史表
    记录系统的更新历史
    """
    id = models.AutoField(primary_key=True, db_comment='主键，自增')
    update_time = models.DateField(auto_now_add=True, db_comment='更新日期，默认服务器系统日期')
    update_content = models.TextField(db_comment='更新内容描述')
    
    class Meta:
        managed = False
        db_table = 'update_history'
        indexes = [
            models.Index(fields=['update_time'], name='idx_update_time'),  # 按日期排序
        ]
    
    def __str__(self):
        return f"Update {self.id} at {self.update_time}"