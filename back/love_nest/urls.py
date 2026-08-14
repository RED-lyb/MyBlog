"""
爱情小窝 URL 配置
"""
from django.urls import path

from . import views

urlpatterns = [
    path('config/', views.get_config, name='love_nest_get_config'),
    path('config/update/', views.update_config, name='love_nest_update_config'),
    path('config/members/', views.update_members, name='love_nest_update_members'),
    path('editor/check/', views.check_editor, name='love_nest_check_editor'),
    path('photos/decor/', views.list_decor_photos, name='love_nest_list_decor_photos'),
    path('photos/', views.get_photos, name='love_nest_get_photos'),
    path('photos/upload/', views.upload_photo, name='love_nest_upload_photo'),
    path('photos/<int:photo_id>/update/', views.update_photo, name='love_nest_update_photo'),
    path('photos/<int:photo_id>/delete/', views.delete_photo, name='love_nest_delete_photo'),
    path('diaries/', views.get_diaries, name='love_nest_get_diaries'),
    path('diaries/create/', views.create_diary, name='love_nest_create_diary'),
    path('diaries/<int:diary_id>/update/', views.update_diary, name='love_nest_update_diary'),
    path('diaries/<int:diary_id>/delete/', views.delete_diary, name='love_nest_delete_diary'),
    path('milestones/', views.get_milestones, name='love_nest_get_milestones'),
    path('milestones/create/', views.create_milestone, name='love_nest_create_milestone'),
    path('milestones/<int:milestone_id>/update/', views.update_milestone, name='love_nest_update_milestone'),
    path('milestones/<int:milestone_id>/delete/', views.delete_milestone, name='love_nest_delete_milestone'),
    path('travel/', views.get_travel, name='love_nest_get_travel'),
    path('travel/<int:city_id>/', views.get_travel_city, name='love_nest_get_travel_city'),
    path('travel/create/', views.create_travel_city, name='love_nest_create_travel_city'),
    path('travel/<int:city_id>/update/', views.update_travel_city, name='love_nest_update_travel_city'),
    path('travel/<int:city_id>/delete/', views.delete_travel_city, name='love_nest_delete_travel_city'),
]
