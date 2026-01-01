"""
Admin configuration for Collection model.
"""

from django.contrib import admin
from apps.collections.models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent', 'master', 'amount', 'status', 'due_date', 'paid_at', 'created_at')
    list_filter = ('status', 'payment_method', 'master', 'created_at', 'due_date')
    search_fields = ('agent__name', 'agent__whatsapp_number', 'transaction_reference', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

