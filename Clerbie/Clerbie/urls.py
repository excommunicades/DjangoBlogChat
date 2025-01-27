"""
URL configuration for Clerbie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView



urlpatterns = [

    # System
    # path('admin/', admin.site.urls),

    # Apps
    path('auth/', include('authify.urls')),
    path('profile/', include('profile.urls')),
    path('users/', include('users.urls')),

    # swagger
    path('api_schema', get_schema_view(title='Swagger', description='Guide for the REST API'), name='api_schema'),
    path('swagger/', TemplateView.as_view(
                        template_name='docs.html',
                        extra_context={'schema_url':'api_schema'}
                        ), name='swagger-ui'),

    # test pages
    path('test', TemplateView.as_view(
                        template_name='websocket.html'), name='user_chat'),
    path('test2', TemplateView.as_view(
                        template_name='websocket2.html'), name='user_chat'),

]

