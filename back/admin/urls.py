"""
管理员应用 URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 统计数据
    path('statistics/', views.get_statistics, name='admin_statistics'),
    
    # 文章管理
    path('articles/', views.list_articles, name='admin_list_articles'),
    path('articles/<int:article_id>/', views.get_article, name='admin_get_article'),
    path('articles/create/', views.create_article, name='admin_create_article'),
    path('articles/<int:article_id>/update/', views.update_article, name='admin_update_article'),
    path('articles/<int:article_id>/delete/', views.delete_article, name='admin_delete_article'),
    
    # 用户管理
    path('users/', views.list_users, name='admin_list_users'),
    path('users/<int:user_id>/', views.get_user, name='admin_get_user'),
    path('users/<int:user_id>/update/', views.update_user, name='admin_update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='admin_delete_user'),
    path('users/<int:user_id>/toggle-admin/', views.toggle_admin, name='admin_toggle_admin'),
    
    # 网盘管理
    path('network-files/', views.list_network_files, name='admin_list_network_files'),
    path('network-files/delete/', views.delete_network_file, name='admin_delete_network_file'),
    
    # 全局配置
    path('config/', views.get_config, name='admin_get_config'),
    path('config/update/', views.update_config, name='admin_update_config'),
]

