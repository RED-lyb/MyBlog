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
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(db_comment='用户ID')
    token_hash = models.CharField(max_length=64, db_comment='Refresh Token的哈希值')
    expires_at = models.DateTimeField(db_comment='过期时间')
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
        """检查token是否过期"""
        return timezone.now() > self.expires_at
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
