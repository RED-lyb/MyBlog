"""
反馈应用 URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 公开接口：获取反馈列表（不需要登录）
    path('list/', views.get_feedback_list, name='get_feedback_list'),
    
    # 用户接口：创建反馈
    path('create/', views.create_feedback, name='create_feedback'),
    # 用户接口：更新自己的反馈
    path('<int:feedback_id>/update/', views.update_my_feedback, name='update_my_feedback'),
    # 用户接口：删除自己的反馈
    path('<int:feedback_id>/delete/', views.delete_my_feedback, name='delete_my_feedback'),
    
    # 管理员接口
    path('admin/list/', views.admin_get_feedback_list, name='admin_get_feedback_list'),
    path('admin/<int:feedback_id>/', views.admin_get_feedback, name='admin_get_feedback'),
    path('admin/<int:feedback_id>/update-status/', views.admin_update_feedback_status, name='admin_update_feedback_status'),
    path('admin/<int:feedback_id>/delete/', views.admin_delete_feedback, name='admin_delete_feedback'),
]

