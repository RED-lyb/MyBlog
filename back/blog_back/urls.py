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
from home.views import home
from register.views import register
from forgot.views import forgot
from login.views import login
from common.captcha_views import get_captcha, verify_captcha
from common.auth_views import refresh_token, logout

urlpatterns = [
    path('captcha/', include('captcha.urls')),
    path('api/home/', home),
    path('api/register/', register),
    path('api/forgot/', forgot),
    path('api/login/', login),
    path('api/captcha/', get_captcha),
    path('api/captcha/verify/', verify_captcha),
    # JWT认证相关接口
    path('api/auth/refresh/', refresh_token),
    path('api/auth/logout/', logout),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
