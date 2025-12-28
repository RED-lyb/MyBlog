from django.urls import path
from . import views
from . import comment_views
from . import like_views

urlpatterns = [
    path('list/', views.get_all_articles, name='article_list'),
    path('create/', views.create_article, name='create_article'),
    path('<int:article_id>/', views.get_article_detail, name='article_detail'),
    # 评论相关
    path('<int:article_id>/comments/', comment_views.get_comments, name='get_comments'),
    path('<int:article_id>/comments/create/', comment_views.create_comment, name='create_comment'),
    # 喜欢相关
    path('<int:article_id>/like/', like_views.toggle_like, name='toggle_like'),
    path('<int:article_id>/like/status/', like_views.check_like_status, name='check_like_status'),
]

