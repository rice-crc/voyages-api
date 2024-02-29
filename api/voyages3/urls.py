"""voyages3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include,path,re_path
from django.conf.urls.static import static
from django.conf import settings
from filebrowser.sites import site
from rest_framework.authtoken import views
from rest_framework.schemas import get_schema_view
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('voyage/',include('voyage.urls')),
    path('timelapse/',include('timelapse.urls')),
    path('past/',include('past.urls')),
    path('docs/',include('document.urls')),
    path('assessment/',include('assessment.urls')),
    path('geo/',include('geo.urls')),
    path('blog/',include('blog.urls')),
    path('common/',include('common.urls')),
    path('captcha/', include('captcha.urls')),
    path('filebrowser/', site.urls),
    path('tinymce/', site.urls),
	re_path(r'^_nested_admin/', include('nested_admin.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
    # path('voyages_auth_endpoint/', views.obtain_auth_token)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)