"""
URL configuration for reports app.
"""

from django.urls import path
from apps.reports.views import DashboardView, CollectionsExportView

app_name = 'reports'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('collections/export/', CollectionsExportView.as_view(), name='collections-export'),
]

