"""
Django admin configuration for Master model.
"""

from django.contrib import admin
from apps.masters.models import Master


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    """Admin interface for Master model."""
    list_display = ('name', 'email', 'api_key', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'api_key')
    readonly_fields = ('id', 'api_key', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'email', 'is_active')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'webhook_url', 'webhook_secret')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

