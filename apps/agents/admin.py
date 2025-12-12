"""
Django admin configuration for Agent model.
"""

from django.contrib import admin
from apps.agents.models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Admin interface for Agent model."""
    list_display = ('name', 'whatsapp_number', 'master', 'risk_score', 'is_active', 'created_at')
    list_filter = ('master', 'is_active', 'created_at')
    search_fields = ('name', 'whatsapp_number', 'phone_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'master', 'name', 'whatsapp_number', 'phone_number', 'is_active')
        }),
        ('Risk & Scoring', {
            'fields': ('risk_score',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset by selecting related master."""
        qs = super().get_queryset(request)
        return qs.select_related('master')
