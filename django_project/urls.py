"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from blog.views import Home,Dashboard,CreatePost

urlpatterns = [
    path('login',auth_views.LoginView.as_view(template_name='blog/login.html'),name='login'),
    path('logout',auth_views.LogoutView.as_view(),name='logout'),
    path('',Home.as_view(),name='home_view'),
    path('dashboard',Dashboard.as_view(),name='dashboard'),
    path('admin/', admin.site.urls),
    path('blog/',include('blog.urls')),
    path('post/create/',CreatePost.as_view(), name='add_post'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)