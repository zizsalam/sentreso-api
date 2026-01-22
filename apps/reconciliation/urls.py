"""
URL configuration for reconciliation app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reconciliation.views import PaymentMatchViewSet, ReconciliationRecordViewSet

router = DefaultRouter()
router.register(r'payments', PaymentMatchViewSet, basename='payment-match')
router.register(r'records', ReconciliationRecordViewSet, basename='reconciliation-record')

app_name = 'reconciliation'

urlpatterns = [
    path('', include(router.urls)),
]








