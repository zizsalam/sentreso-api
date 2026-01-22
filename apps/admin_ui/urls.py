"""
URL configuration for admin UI.
"""

from django.urls import path
from apps.admin_ui import views

app_name = 'admin_ui'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.today, name='today'),
    path('today/', views.today, name='today'),
    path('collections/<uuid:collection_id>/', views.collection_detail, name='collection-detail'),
    path('manual-import/', views.manual_import, name='manual-import'),
    path('whatsapp/compose/', views.whatsapp_compose, name='whatsapp-compose'),
    path('payments/', views.all_payments, name='all-payments'),
    path('payments/<uuid:payment_id>/', views.payment_detail, name='payment-detail'),
    path('needs-review/', views.needs_review, name='needs-review'),
    path('agents/', views.agents, name='agents'),
    path('agents/<uuid:agent_id>/', views.agent_detail, name='agent-detail'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout, name='logout'),
]

