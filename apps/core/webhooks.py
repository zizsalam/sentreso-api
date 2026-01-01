"""
Webhook functionality for sending notifications to masters.
"""

import hmac
import hashlib
import json
import requests
from django.conf import settings
from django.utils import timezone


def generate_webhook_signature(payload, secret):
    """
    Generate HMAC SHA256 signature for webhook payload.

    Args:
        payload: The webhook payload (dict or string)
        secret: The webhook secret key

    Returns:
        str: The signature in format 'sha256=...'
    """
    if isinstance(payload, dict):
        payload_str = json.dumps(payload, sort_keys=True)
    else:
        payload_str = payload

    signature = hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return f'sha256={signature}'


def send_webhook(master, event, data, retry_count=0, max_retries=3):
    """
    Send a webhook notification to a master's webhook URL.

    Args:
        master: Master instance
        event: Event type (e.g., 'collection.created', 'collection.paid')
        data: Event data (dict)
        retry_count: Current retry attempt
        max_retries: Maximum number of retries

    Returns:
        bool: True if webhook was sent successfully, False otherwise
    """
    if not master.webhook_url:
        # No webhook URL configured, skip silently
        return False

    payload = {
        'event': event,
        'timestamp': timezone.now().isoformat(),
        'data': data,
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Sentreso-Webhook/1.0',
    }

    # Add signature if webhook secret is configured
    if master.webhook_secret:
        signature = generate_webhook_signature(payload, master.webhook_secret)
        headers['X-Sentreso-Signature'] = signature

    try:
        response = requests.post(
            master.webhook_url,
            json=payload,
            headers=headers,
            timeout=10,  # 10 second timeout
        )
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        # Log error (in production, use proper logging)
        print(f"Webhook error for master {master.id}: {e}")

        # Retry logic (could be improved with exponential backoff)
        if retry_count < max_retries:
            # In production, use a task queue for retries
            # For now, we'll just log the failure
            pass

        return False

