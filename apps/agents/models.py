"""
Agent model - represents mobile money agents/shops who owe payments.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
from apps.masters.models import Master
from apps.agents.managers import AgentManager


class Agent(BaseModel):
    """
    Agent (Mobile Money Agent/Shop) model.

    Agents are entities that owe payments to masters.
    Each agent belongs to a master and has a WhatsApp number for communication.
    """
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='agents')
    name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=20, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Risk score from 0.0 to 100.0'
    )
    is_active = models.BooleanField(default=True)

    objects = AgentManager()

    class Meta:
        ordering = ['-created_at']
        # Ensure whatsapp_number uniqueness per master
        unique_together = [['master', 'whatsapp_number']]
        indexes = [
            models.Index(fields=['master', 'whatsapp_number']),
            models.Index(fields=['master', 'is_active']),
            models.Index(fields=['risk_score']),
        ]

    def __str__(self):
        return f"{self.name} ({self.whatsapp_number}) - {self.master.name}"
