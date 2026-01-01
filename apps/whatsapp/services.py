"""
WhatsApp service for sending messages via WhatsApp Business API.
"""

import requests
from django.conf import settings
from django.utils import timezone
from apps.whatsapp.models import WhatsAppMessage


class WhatsAppService:
    """Service for interacting with WhatsApp Business API."""

    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)

    def send_message(self, message):
        """
        Send a WhatsApp message via the Business API.

        Args:
            message: WhatsAppMessage instance

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.api_url or not self.api_token:
            # WhatsApp API not configured
            return False

        try:
            # Determine if we should use template or text message
            if message.template and message.template.whatsapp_template_name:
                # Use template message
                payload = self._build_template_payload(message)
            else:
                # Use text message (24-hour window only)
                payload = self._build_text_payload(message)

            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
            }

            url = f"{self.api_url}/v1/{self.phone_number_id}/messages"
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            message.message_id = result.get('messages', [{}])[0].get('id')
            message.sent_at = timezone.now()
            return True

        except requests.exceptions.RequestException as e:
            message.error_message = str(e)
            return False
        except Exception as e:
            message.error_message = str(e)
            return False

    def _build_template_payload(self, message):
        """Build payload for template message."""
        template = message.template
        metadata = message.metadata or {}
        template_params = metadata.get('template_params', {})

        # Extract template parameters
        components = []
        if template_params:
            params = []
            for key in ['agent_name', 'amount', 'due_date']:
                if key in template_params:
                    params.append({
                        'type': 'text',
                        'text': str(template_params[key])
                    })

            if params:
                components = [{
                    'type': 'body',
                    'parameters': params
                }]

        payload = {
            'messaging_product': 'whatsapp',
            'to': message.to_number,
            'type': 'template',
            'template': {
                'name': template.whatsapp_template_name,
                'language': {'code': template.language_code},
            }
        }

        if components:
            payload['template']['components'] = components

        return payload

    def _build_text_payload(self, message):
        """Build payload for text message."""
        return {
            'messaging_product': 'whatsapp',
            'to': message.to_number,
            'type': 'text',
            'text': {
                'body': message.content
            }
        }

