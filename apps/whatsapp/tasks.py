"""
Background tasks for WhatsApp message sending.
"""

from django.utils import timezone
from django.conf import settings
from apps.whatsapp.models import WhatsAppMessage, WhatsAppTemplate
from apps.collections.models import Collection
from apps.agents.models import Agent
from apps.masters.models import Master
from apps.whatsapp.services import WhatsAppService


def send_collection_reminder_task(collection_id):
    """
    Task to send a collection reminder via WhatsApp.

    Args:
        collection_id: UUID of the collection
    """
    try:
        collection = Collection.objects.get(id=collection_id)
        agent = collection.agent
        master = collection.master

        # Find active reminder template
        template = WhatsAppTemplate.objects.filter(
            master=master,
            template_type='collection_reminder',
            is_active=True
        ).first()

        # Prepare message content
        if template:
            # Use template with variables
            context = {
                'agent_name': agent.name,
                'amount': str(collection.amount),
                'due_date': collection.due_date.strftime('%Y-%m-%d') if collection.due_date else '',
            }
            content = template.render(context)
            template_obj = template
        else:
            # Fallback to default message
            content = (
                f"Bonjour {agent.name},\n\n"
                f"Rappel: Vous avez un paiement en attente de {collection.amount} FCFA.\n"
                f"Date d'échéance: {collection.due_date.strftime('%Y-%m-%d') if collection.due_date else 'N/A'}\n\n"
                f"Merci de régulariser votre compte."
            )
            template_obj = None

        # Create message record
        message = WhatsAppMessage.objects.create(
            master=master,
            agent=agent,
            collection=collection,
            template=template_obj,
            direction='outbound',
            status='pending',
            to_number=agent.whatsapp_number,
            content=content,
            metadata={
                'template_used': template.whatsapp_template_name if template else None,
                'template_params': context if template else {},
            }
        )

        # Send via WhatsApp service
        service = WhatsAppService()
        success = service.send_message(message)

        if success:
            message.status = 'sent'
            message.sent_at = timezone.now()
            collection.last_reminder_sent = timezone.now()
            collection.save()
        else:
            message.status = 'failed'
            message.error_message = "WhatsApp API not configured. Set WHATSAPP_API_URL and WHATSAPP_API_TOKEN in settings."

        message.save()

        return {'success': success, 'message_id': str(message.id)}

    except Exception as e:
        # Log error
        print(f"Error sending collection reminder: {e}")
        return {'success': False, 'error': str(e)}


def send_whatsapp_message_task(master_id, agent_id, content):
    """
    Task to send a custom WhatsApp message.

    Args:
        master_id: UUID of the master
        agent_id: UUID of the agent
        content: Message content
    """
    try:
        master = Master.objects.get(id=master_id)
        agent = Agent.objects.get(id=agent_id, master=master)

        # Create message record
        message = WhatsAppMessage.objects.create(
            master=master,
            agent=agent,
            direction='outbound',
            status='pending',
            to_number=agent.whatsapp_number,
            content=content,
        )

        # Send via WhatsApp service
        service = WhatsAppService()
        success = service.send_message(message)

        if success:
            message.status = 'sent'
            message.sent_at = timezone.now()
        else:
            message.status = 'failed'
            message.error_message = "WhatsApp API not configured. Set WHATSAPP_API_URL and WHATSAPP_API_TOKEN in settings."

        message.save()

        return {'success': success, 'message_id': str(message.id)}

    except Exception as e:
        # Log error
        print(f"Error sending WhatsApp message: {e}")
        return {'success': False, 'error': str(e)}

