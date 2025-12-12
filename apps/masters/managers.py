"""
Custom managers for Master model.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class MasterManager(models.Manager):
    """Custom manager for Master model."""

    def get_active(self):
        """Return only active masters."""
        return self.filter(is_active=True)

    def get_by_api_key(self, api_key):
        """
        Get master by API key.

        Args:
            api_key: The API key to look up

        Returns:
            Master instance

        Raises:
            Master.DoesNotExist: If no master found with the given API key
        """
        try:
            return self.get(api_key=api_key, is_active=True)
        except ObjectDoesNotExist:
            raise self.model.DoesNotExist(f"No active master found with API key: {api_key}")
