"""
URL configuration for whatsapp app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.whatsapp.views import WhatsAppTemplateViewSet, WhatsAppMessageViewSet

router = DefaultRouter()
router.register(r'templates', WhatsAppTemplateViewSet, basename='whatsapp-template')
router.register(r'messages', WhatsAppMessageViewSet, basename='whatsapp-message')

app_name = 'whatsapp'

urlpatterns = [
    path('', include(router.urls)),
]

