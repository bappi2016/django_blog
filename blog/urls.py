from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import Home,\
    PostDetail,\
    CreatePost,\
    UpdatePost,\
    PostDelete,\
    PostCategory,\
    UserCategory



app_name = 'blog'

urlpatterns = [
    path('',Home.as_view(),name='home_view'),
    path('<slug:slug>/',PostDetail.as_view(),name='postdetail'),
    path('<slug:slug>/update/',UpdatePost.as_view(),name='post_update'),
    path('category/<int:pk>/',PostCategory.as_view(),name='post_by_category'),
    path('user/<int:pk>/',UserCategory.as_view(),name='post_by_user'),
    path('<slug:slug>/delete/',PostDelete.as_view(),name='article-delete'),
]
