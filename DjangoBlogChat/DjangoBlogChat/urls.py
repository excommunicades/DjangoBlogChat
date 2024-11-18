"""
URL configuration for DjangoBlogChat project.

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
from rest_framework.schemas import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from django.views.generic import TemplateView


from django.contrib import admin
from django.urls import path, include

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Blog API",
#         default_version='v1',
#         description="API for user registration, login, and password recovery",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="contact@blogapi.com"),
#         license=openapi.License(name="MIT License"),
#     ),
#     public=True,
#     permission_classes=(AllowAny,),
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('blog_user.urls')),
    path('api/', include('api.settings.urls')),

    path('api_schema', get_schema_view(title='Swagger', description='Guide for the REST API'), name='api_schema'),
    path('swagger', TemplateView.as_view(
                        template_name='docs.html',
                        extra_context={'schema_url':'api_schema'}
                        ), name='swagger-ui'),
]
