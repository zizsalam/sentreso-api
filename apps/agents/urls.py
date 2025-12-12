"""
URL routing for Agent API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.agents.views import AgentViewSet

router = DefaultRouter()
router.register(r'', AgentViewSet, basename='agent')

urlpatterns = [
    path('', include(router.urls)),
]
