"""
URL configuration for Sentreso project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Admin site configuration
admin.site.site_header = 'Sentreso Admin'
admin.site.site_title = 'Sentreso Admin Portal'
admin.site.index_title = 'Welcome to Sentreso Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/', include('apps.api.urls')),
]
