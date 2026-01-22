"""
URL configuration for collections app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.collections.views import CollectionViewSet

router = DefaultRouter()
router.register(r'', CollectionViewSet, basename='collection')

app_name = 'collections'

urlpatterns = [
    path('', include(router.urls)),
]








