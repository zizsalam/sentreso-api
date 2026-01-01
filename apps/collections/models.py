"""
Collection model - represents payment obligations from agents to masters.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import BaseModel
from apps.masters.models import Master
from apps.agents.models import Agent
from apps.collections.managers import CollectionManager


class Collection(BaseModel):
    """
    Collection model - represents a payment obligation.

    A collection is created when a master expects payment from an agent.
    The collection goes through different statuses: pending -> paid/failed/cancelled.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='collections')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='collections')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Amount to be collected'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        help_text='Method used for payment'
    )
    transaction_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text='External transaction reference (e.g., MTN20241228123456)'
    )
    due_date = models.DateTimeField(help_text='Date when payment is due')
    paid_at = models.DateTimeField(blank=True, null=True, help_text='When payment was received')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes')
    last_reminder_sent = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last time a reminder was sent for this collection'
    )

    objects = CollectionManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['master', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['transaction_reference']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.amount} FCFA - {self.get_status_display()}"

    def mark_as_paid(self, transaction_reference=None, payment_method=None, notes=None):
        """
        Mark this collection as paid.

        Args:
            transaction_reference: External transaction reference
            payment_method: Method used for payment
            notes: Additional notes
        """
        from django.utils import timezone
        self.status = 'paid'
        self.paid_at = timezone.now()
        if transaction_reference:
            self.transaction_reference = transaction_reference
        if payment_method:
            self.payment_method = payment_method
        if notes:
            if self.notes:
                self.notes += f"\n{notes}"
            else:
                self.notes = notes
        self.save()

    def mark_as_failed(self, notes=None):
        """Mark this collection as failed."""
        self.status = 'failed'
        if notes:
            if self.notes:
                self.notes += f"\n{notes}"
            else:
                self.notes = notes
        self.save()

    def cancel(self, notes=None):
        """Cancel this collection."""
        self.status = 'cancelled'
        if notes:
            if self.notes:
                self.notes += f"\n{notes}"
            else:
                self.notes = notes
        self.save()

    def is_overdue(self):
        """Check if the collection is overdue."""
        from django.utils import timezone
        return self.status == 'pending' and self.due_date < timezone.now()

