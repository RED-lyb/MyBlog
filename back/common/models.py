# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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
