"""
网盘应用 URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_files, name='list_files'),  # 获取文件列表
    path('upload/', views.upload_file, name='upload_file'),  # 上传文件
    path('download/<path:file_path>', views.download_file, name='download_file'),  # 下载文件
    path('delete/<path:file_path>', views.delete_file, name='delete_file'),  # 删除文件
    path('mkdir/', views.create_directory, name='create_directory'),  # 创建目录
]

