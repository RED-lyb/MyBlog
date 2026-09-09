from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.cinema_list, name='cinema_list'),
    path('stream/status/', views.stream_status, name='cinema_stream_status'),
    path('admin/list/', views.admin_cinema_list, name='cinema_admin_list'),
    path('admin/upload/', views.admin_upload_cinema, name='cinema_admin_upload'),
    path('admin/<str:filename>/info/', views.admin_cinema_info, name='cinema_admin_info'),
    path('admin/<str:filename>/delete/', views.admin_delete_cinema, name='cinema_admin_delete'),
    path('admin/stream/start/', views.admin_start_stream, name='cinema_admin_start'),
    path('admin/stream/stop/', views.admin_stop_stream, name='cinema_admin_stop'),
    path('admin/transcode/start/', views.admin_start_transcode, name='cinema_admin_transcode'),
    path('admin/runtime/', views.admin_runtime_info, name='cinema_admin_runtime'),
    path('admin/config/', views.admin_cinema_config, name='cinema_admin_config'),
    path('mtx/webrtc/<path:subpath>', views.mediamtx_webrtc_proxy, name='cinema_mtx_webrtc_proxy'),
]
