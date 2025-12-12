"""
Custom managers for Agent model.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class AgentManager(models.Manager):
    """Custom manager for Agent model."""

    def get_active(self):
        """Return only active agents."""
        return self.filter(is_active=True)

    def get_by_master(self, master):
        """Get agents for a specific master."""
        return self.filter(master=master, is_active=True)

    def get_by_whatsapp(self, whatsapp_number, master):
        """
        Get agent by WhatsApp number for a specific master.

        Args:
            whatsapp_number: The WhatsApp number to look up
            master: The master instance

        Returns:
            Agent instance

        Raises:
            Agent.DoesNotExist: If no agent found
        """
        try:
            return self.get(whatsapp_number=whatsapp_number, master=master, is_active=True)
        except ObjectDoesNotExist:
            raise self.model.DoesNotExist(
                f"No active agent found with WhatsApp number {whatsapp_number} for master {master.id}"
            )
