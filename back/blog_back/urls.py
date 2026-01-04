"""
URL configuration for blog_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import home, avatar_resource
from register.views import register
from forgot.views import forgot
from login.views import login
from common.captcha_views import get_captcha, verify_captcha, get_captcha_image
from common.auth_views import refresh_token, logout
from common.views import (
    get_user_info, get_user_by_id, toggle_follow, check_follow_status,
    upload_avatar, update_profile, reset_password,
    get_user_following_list, get_user_followers_list,
    get_user_liked_articles_list, get_user_articles_list
)

urlpatterns = [
    path('captcha/', include('captcha.urls')),
    path('api/home/', home),
    path('api/home/avatar/', avatar_resource),
    path('api/register/', register),
    path('api/forgot/', forgot),
    path('api/login/', login),
    path('api/captcha/', get_captcha),
    path('api/captcha/image/<str:key>/', get_captcha_image, name='captcha-image'),
    path('api/captcha/verify/', verify_captcha),
    path('api/auth/refresh/', refresh_token),
    path('api/auth/logout/', logout),
    path('api/user/info/', get_user_info),
    path('api/user/<int:user_id>/', get_user_by_id, name='get_user_by_id'),  # 根据ID获取用户信息
    path('api/user/<int:user_id>/follow/', toggle_follow, name='toggle_follow'),  # 关注/取消关注
    path('api/user/<int:user_id>/follow-status/', check_follow_status, name='check_follow_status'),  # 检查关注状态
    path('api/user/avatar/upload/', upload_avatar, name='upload_avatar'),  # 上传头像
    path('api/user/profile/', update_profile, name='update_profile'),  # 更新资料
    path('api/user/password/reset/', reset_password, name='reset_password'),  # 重设密码
    path('api/user/<int:user_id>/following/', get_user_following_list, name='get_user_following_list'),  # 获取关注列表
    path('api/user/<int:user_id>/followers/', get_user_followers_list, name='get_user_followers_list'),  # 获取粉丝列表
    path('api/user/<int:user_id>/liked-articles/', get_user_liked_articles_list, name='get_user_liked_articles_list'),  # 获取喜欢的文章列表
    path('api/user/<int:user_id>/articles/', get_user_articles_list, name='get_user_articles_list'),  # 获取发布的文章列表
    path('api/article/', include('article.urls')),  # 文章相关路由
    path('api/network_disk/', include('network_disk.urls')),  # 网盘相关路由
    path('api/admin/', include('admin.urls')),  # 管理员相关路由
    path('api/history/', include('history.urls')),  # 更新历史相关路由
    path('api/feedback/', include('feedback.urls')),  # 反馈相关路由
]