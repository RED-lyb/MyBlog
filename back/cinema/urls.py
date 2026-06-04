from django.urls import path

from . import views

urlpatterns = [
    path('get/token', views.get_token, name='cinema_get_token'),
    path('list/', views.cinema_list, name='cinema_list'),
    path('stream/status/', views.stream_status, name='cinema_stream_status'),
    path('admin/list/', views.admin_cinema_list, name='cinema_admin_list'),
    path('admin/upload/', views.admin_upload_cinema, name='cinema_admin_upload'),
    path('admin/<str:filename>/delete/', views.admin_delete_cinema, name='cinema_admin_delete'),
    path('admin/stream/start/', views.admin_start_stream, name='cinema_admin_start'),
    path('admin/stream/stop/', views.admin_stop_stream, name='cinema_admin_stop'),
    path('admin/runtime/', views.admin_runtime_info, name='cinema_admin_runtime'),
]
