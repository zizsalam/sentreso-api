"""
URL routing for Master API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.masters.views import MasterViewSet

router = DefaultRouter()
router.register(r'', MasterViewSet, basename='master')

urlpatterns = [
    path('', include(router.urls)),
]

