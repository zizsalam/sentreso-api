"""
URL configuration for Sentreso project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from sentreso.views import root, homepage

# Admin site configuration
admin.site.site_header = 'Sentreso Admin'
admin.site.site_title = 'Sentreso Admin Portal'
admin.site.index_title = 'Welcome to Sentreso Administration'

urlpatterns = [
    path('', homepage, name='homepage'),
    path('api/', root, name='api-root'),  # JSON API root for API clients
    path('admin/', admin.site.urls),  # Django admin
    path('admin-ui/', include('apps.admin_ui.urls')),  # Custom admin UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/', include('apps.api.urls')),
]
