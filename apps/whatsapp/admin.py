"""
Admin configuration for WhatsApp models.
"""

from django.contrib import admin
from apps.whatsapp.models import WhatsAppTemplate, WhatsAppMessage


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'master', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'master', 'created_at')
    search_fields = ('name', 'whatsapp_template_name', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'master', 'agent', 'direction', 'status', 'to_number', 'sent_at', 'created_at')
    list_filter = ('direction', 'status', 'master', 'created_at')
    search_fields = ('to_number', 'from_number', 'content', 'message_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

