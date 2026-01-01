"""
Admin configuration for Reconciliation models.
"""

from django.contrib import admin
from apps.reconciliation.models import PaymentMatch, ReconciliationRecord


@admin.register(PaymentMatch)
class PaymentMatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'master', 'agent', 'amount', 'is_matched', 'matched_collection', 'received_at', 'created_at')
    list_filter = ('is_matched', 'payment_method', 'master', 'created_at')
    search_fields = ('transaction_reference', 'agent__name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ReconciliationRecord)
class ReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'master', 'agent', 'status', 'matched_payments', 'unmatched_payments', 'started_at', 'completed_at')
    list_filter = ('status', 'master', 'started_at')
    search_fields = ('notes', 'error_message')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'started_at'

