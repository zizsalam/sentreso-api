"""
Reconciliation models for matching payments to collections.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import BaseModel
from apps.masters.models import Master
from apps.agents.models import Agent
from apps.collections.models import Collection


class PaymentMatch(BaseModel):
    """
    PaymentMatch model - represents a payment received that needs to be matched to a collection.

    When a payment is received, it's recorded as a PaymentMatch with is_matched=False.
    The reconciliation process matches it to a collection and sets is_matched=True.
    """

    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='payment_matches')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='payment_matches')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Amount received'
    )
    transaction_reference = models.CharField(
        max_length=255,
        db_index=True,
        help_text='External transaction reference (e.g., MTN20241228123456)'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        help_text='Method used for payment'
    )
    received_at = models.DateTimeField(help_text='When payment was received')
    is_matched = models.BooleanField(default=False, db_index=True, help_text='Whether payment has been matched to a collection')
    matched_collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        related_name='payment_matches',
        null=True,
        blank=True,
        help_text='Collection this payment was matched to'
    )
    matched_at = models.DateTimeField(blank=True, null=True, help_text='When payment was matched')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['master', 'is_matched']),
            models.Index(fields=['agent', 'is_matched']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['is_matched', 'received_at']),
        ]

    def __str__(self):
        status = "Matched" if self.is_matched else "Unmatched"
        return f"{self.agent.name} - {self.amount} FCFA - {status}"


class ReconciliationRecord(BaseModel):
    """
    ReconciliationRecord model - represents a reconciliation run.

    Tracks when reconciliation was performed and its results.
    """

    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reconciliation_records')
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='reconciliation_records',
        null=True,
        blank=True,
        help_text='If set, reconciliation was for this agent only'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(help_text='When reconciliation started')
    completed_at = models.DateTimeField(blank=True, null=True, help_text='When reconciliation completed')
    total_payments = models.IntegerField(default=0, help_text='Total payments processed')
    matched_payments = models.IntegerField(default=0, help_text='Number of payments matched')
    unmatched_payments = models.IntegerField(default=0, help_text='Number of payments not matched')
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total amount processed'
    )
    error_message = models.TextField(blank=True, null=True, help_text='Error message if reconciliation failed')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['master', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['status', 'started_at']),
        ]

    def __str__(self):
        return f"Reconciliation {self.id} - {self.get_status_display()}"








