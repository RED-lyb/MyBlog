from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.get_all_articles, name='article_list'),
    path('<int:article_id>/', views.get_article_detail, name='article_detail'),
]

