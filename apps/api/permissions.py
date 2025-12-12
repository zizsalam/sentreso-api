"""
Custom permissions for Sentreso API.
"""

from rest_framework import permissions


class IsAuthenticatedWithAPIKey(permissions.BasePermission):
    """
    Permission class to check if request is authenticated with API key.

    This ensures that request.master is set by APIKeyAuthentication.
    """

    def has_permission(self, request, view):
        # Check if master is attached to request (set by APIKeyAuthentication)
        return hasattr(request, 'auth') and request.auth is not None
