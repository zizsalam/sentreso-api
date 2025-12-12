"""
Master model - represents suppliers/lenders who collect payments.
"""

from django.db import models
from django.core.validators import URLValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.core.models import BaseModel
from apps.core.utils import generate_api_key
from apps.masters.managers import MasterManager


class Master(BaseModel):
    """
    Master (Supplier/Lender) model.

    Masters are the entities that need to collect payments from agents.
    Each master has an API key for authentication.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    api_key = models.CharField(max_length=255, unique=True, db_index=True)
    webhook_url = models.URLField(max_length=500, blank=True, null=True, validators=[URLValidator()])
    webhook_secret = models.CharField(max_length=255, blank=True, null=True, help_text='Secret for HMAC webhook signing')
    is_active = models.BooleanField(default=True)

    objects = MasterManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_key']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def generate_api_key(self):
        """Generate a new API key for this master."""
        from django.conf import settings
        prefix = getattr(settings, 'API_KEY_PREFIX_LIVE', 'sk_live_')
        self.api_key = generate_api_key(prefix)
        return self.api_key


@receiver(pre_save, sender=Master)
def generate_api_key_if_needed(sender, instance, **kwargs):
    """
    Signal to auto-generate API key if not provided when creating a new master.
    """
    if not instance.api_key:
        instance.generate_api_key()
