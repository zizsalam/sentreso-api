"""
Utility functions for Sentreso.
"""

import secrets
from django.conf import settings


def generate_api_key(prefix=None):
    """
    Generate a random API key.

    Args:
        prefix: Optional prefix for the API key (e.g., 'sk_live_' or 'sk_test_')

    Returns:
        str: Generated API key
    """
    # Generate 32 random bytes (256 bits) and encode as hex (64 characters)
    random_part = secrets.token_hex(32)

    if prefix:
        return f"{prefix}{random_part}"

    return random_part
