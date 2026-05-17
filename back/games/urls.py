"""
游戏应用 URL 配置
"""
from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.get_games_list, name='get_games_list'),
    path('public/<int:game_id>/', views.get_game_public, name='get_game_public'),
    path(
        'download/<int:game_id>/<str:platform>/',
        views.download_platform_file,
        name='download_platform_file',
    ),
    path('admin/list/', views.admin_get_games_list, name='admin_get_games_list'),
    path('admin/create/', views.admin_create_game, name='admin_create_game'),
    path('admin/<int:game_id>/', views.admin_get_game, name='admin_get_game'),
    path(
        'admin/<int:game_id>/upload-image/',
        views.admin_upload_game_image,
        name='admin_upload_game_image',
    ),
    path(
        'admin/<int:game_id>/upload-web-zip/',
        views.admin_upload_web_zip,
        name='admin_upload_web_zip',
    ),
    path(
        'admin/<int:game_id>/upload-platform/',
        views.admin_upload_platform_file,
        name='admin_upload_platform_file',
    ),
    path('admin/<int:game_id>/update/', views.admin_update_game, name='admin_update_game'),
    path('admin/<int:game_id>/delete/', views.admin_delete_game, name='admin_delete_game'),
]
