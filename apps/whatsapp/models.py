"""
WhatsApp models for message templates and message tracking.
"""

from django.db import models
from apps.core.models import BaseModel
from apps.masters.models import Master
from apps.agents.models import Agent
from apps.collections.models import Collection


class WhatsAppTemplate(BaseModel):
    """
    WhatsApp message template model.

    Templates define reusable message formats that can be sent to agents.
    Templates can use variables that are replaced with actual values when sending.
    """

    TEMPLATE_TYPE_CHOICES = [
        ('collection_reminder', 'Collection Reminder'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('custom', 'Custom'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='whatsapp_templates')
    name = models.CharField(max_length=255, help_text='Template name for internal reference')
    whatsapp_template_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Name of the approved template in Meta Business Suite'
    )
    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_TYPE_CHOICES,
        default='custom',
        help_text='Type of template'
    )
    content = models.TextField(help_text='Template content with variables like {agent_name}, {amount}, etc.')
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text='Variable definitions (e.g., {"agent_name": "Agent Name", "amount": "Amount"})'
    )
    language_code = models.CharField(
        max_length=10,
        default='fr',
        help_text='Language code (e.g., fr, en)'
    )
    is_active = models.BooleanField(default=True, help_text='Whether this template is active')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['master', 'is_active']),
            models.Index(fields=['template_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.master.name})"

    def render(self, context):
        """
        Render the template with the given context.

        Args:
            context: Dictionary of variable values

        Returns:
            str: Rendered message content
        """
        content = self.content
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        return content


class WhatsAppMessage(BaseModel):
    """
    WhatsApp message model for tracking all messages sent and received.
    """

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('received', 'Received'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='whatsapp_messages')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='whatsapp_messages', null=True, blank=True)
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        related_name='whatsapp_messages',
        null=True,
        blank=True
    )
    template = models.ForeignKey(
        WhatsAppTemplate,
        on_delete=models.SET_NULL,
        related_name='messages',
        null=True,
        blank=True
    )
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='outbound')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    to_number = models.CharField(max_length=20, help_text='Recipient phone number')
    from_number = models.CharField(max_length=20, blank=True, null=True, help_text='Sender phone number')
    message_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text='WhatsApp message ID from API'
    )
    content = models.TextField(help_text='Message content')
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True, help_text='Error message if sending failed')
    metadata = models.JSONField(default=dict, blank=True, help_text='Additional metadata')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['master', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['collection', 'status']),
            models.Index(fields=['message_id']),
            models.Index(fields=['to_number', 'status']),
        ]

    def __str__(self):
        return f"{self.direction} - {self.to_number} - {self.get_status_display()}"

