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
from common.views import get_user_info, get_user_by_id

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
    path('api/article/', include('article.urls')),  # 文章相关路由
    path('api/network_disk/', include('network_disk.urls')),  # 网盘相关路由
    path('api/admin/', include('admin.urls')),  # 管理员相关路由
]