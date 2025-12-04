from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.get_all_articles, name='article_list'),
]

