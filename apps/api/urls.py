"""
API v1 URL routing.
"""

from django.urls import path, include
from apps.api.views import HealthCheckView

app_name = 'api'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('masters/', include('apps.masters.urls')),
    path('agents/', include('apps.agents.urls')),
    path('collections/', include('apps.collections.urls')),
    path('whatsapp/', include('apps.whatsapp.urls')),
    path('reconciliation/', include('apps.reconciliation.urls')),
    path('reports/', include('apps.reports.urls')),
]

