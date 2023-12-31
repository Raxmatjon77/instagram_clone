"""
URL configuration for instagram_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
scheme_view=get_schema_view(
    openapi.Info(
        title='Instagram Clone (Raxmatjon Hamidov)',
        default_version='v1',
        discription='Instagram Project',
        terms_of_service='demo.com',
        contact=openapi.Contact(email='raxmatjonhamidov242@gmail.com'),
        license=openapi.License(name='Super license(Issued by KHamidovs)'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,]
)

urlpatterns = [
    #swagger
    path('', scheme_view.with_ui(
        'swagger', cache_timeout=0), name='swagger-swagger-ui'),


    path('admin/', admin.site.urls),
    path('users/',include('users.urls')),
    path('post/',include("post.urls")),
]
