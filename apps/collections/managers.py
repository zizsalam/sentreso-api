"""
Custom managers for Collection model.
"""

from django.db import models
from django.utils import timezone


class CollectionManager(models.Manager):
    """Custom manager for Collection model."""

    def get_by_master(self, master):
        """Get all collections for a specific master."""
        return self.filter(master=master)

    def get_pending(self, master=None):
        """Get all pending collections, optionally filtered by master."""
        queryset = self.filter(status='pending')
        if master:
            queryset = queryset.filter(master=master)
        return queryset

    def get_overdue(self, master=None):
        """Get all overdue collections."""
        queryset = self.filter(status='pending', due_date__lt=timezone.now())
        if master:
            queryset = queryset.filter(master=master)
        return queryset

    def get_paid(self, master=None):
        """Get all paid collections."""
        queryset = self.filter(status='paid')
        if master:
            queryset = queryset.filter(master=master)
        return queryset

