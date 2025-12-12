"""
API v1 URL routing.
"""

from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('masters/', include('apps.masters.urls')),
    path('agents/', include('apps.agents.urls')),
]

