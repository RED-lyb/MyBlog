"""
更新历史应用 URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 公开接口：获取更新历史列表
    path('list/', views.get_update_history_list, name='get_update_history_list'),
    
    # 管理员接口
    path('admin/list/', views.admin_get_update_history_list, name='admin_get_update_history_list'),
    path('admin/<int:history_id>/', views.admin_get_update_history, name='admin_get_update_history'),
    path('admin/create/', views.admin_create_update_history, name='admin_create_update_history'),
    path('admin/<int:history_id>/update/', views.admin_update_update_history, name='admin_update_update_history'),
    path('admin/<int:history_id>/delete/', views.admin_delete_update_history, name='admin_delete_update_history'),
]

