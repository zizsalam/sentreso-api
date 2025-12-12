"""
API Key authentication for Sentreso.
"""

from rest_framework import authentication, exceptions
from apps.masters.models import Master


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key authentication.

    Extracts API key from Authorization header:
    Authorization: Bearer sk_live_...
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return None

        try:
            # Extract Bearer token
            scheme, api_key = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return None
        except ValueError:
            return None

        try:
            master = Master.objects.get_by_api_key(api_key)
            if not master.is_active:
                raise exceptions.AuthenticationFailed('API key is inactive.')
        except Master.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')

        # Return (user, auth) tuple - we use None for user since we're not using Django users
        # Also attach master to request for easy access in views
        request.master = master
        return (None, master)
