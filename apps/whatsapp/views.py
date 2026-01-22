"""
API views for WhatsApp models.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.api.permissions import IsAuthenticatedWithAPIKey
from django_rq import get_queue
from apps.whatsapp.models import WhatsAppTemplate, WhatsAppMessage
from apps.whatsapp.serializers import (
    WhatsAppTemplateSerializer,
    WhatsAppMessageSerializer,
    SendReminderSerializer,
    SendMessageSerializer
)
from apps.collections.models import Collection
from apps.agents.models import Agent
from apps.whatsapp.tasks import send_collection_reminder_task, send_whatsapp_message_task


class WhatsAppTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for WhatsAppTemplate management."""
    serializer_class = WhatsAppTemplateSerializer
    permission_classes = [IsAuthenticatedWithAPIKey]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'whatsapp_template_name', 'content']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter templates to only those belonging to the authenticated master."""
        master = getattr(self.request, 'master', self.request.auth)
        queryset = WhatsAppTemplate.objects.filter(master=master)

        # Filter by template_type
        template_type = self.request.query_params.get('template_type', None)
        if template_type:
            queryset = queryset.filter(template_type=template_type)

        # Filter by is_active
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset


class WhatsAppMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing WhatsAppMessage records (read-only)."""
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticatedWithAPIKey]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['to_number', 'from_number', 'content', 'message_id']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter messages to only those belonging to the authenticated master."""
        master = getattr(self.request, 'master', self.request.auth)
        queryset = WhatsAppMessage.objects.filter(master=master)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by agent_id
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        # Filter by collection_id
        collection_id = self.request.query_params.get('collection_id', None)
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)

        # Filter by direction
        direction = self.request.query_params.get('direction', None)
        if direction:
            queryset = queryset.filter(direction=direction)

        return queryset

    @action(detail=False, methods=['post'])
    def send_reminder(self, request):
        """
        Send a collection reminder via WhatsApp.

        POST /api/v1/whatsapp/messages/send_reminder/
        """
        serializer = SendReminderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        collection_id = serializer.validated_data['collection_id']
        collection = Collection.objects.get(id=collection_id, master=request.master)

        # Queue the task
        queue = get_queue('default')
        job = queue.enqueue(send_collection_reminder_task, collection_id=str(collection.id))

        return Response(
            {'message': 'Collection reminder queued for sending'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def send(self, request):
        """
        Send a custom WhatsApp message.

        POST /api/v1/whatsapp/messages/send/
        """
        serializer = SendMessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        agent_id = serializer.validated_data['agent_id']
        content = serializer.validated_data['content']
        agent = Agent.objects.get(id=agent_id, master=request.master)

        # Queue the task
        queue = get_queue('default')
        job = queue.enqueue(
            send_whatsapp_message_task,
            master_id=str(request.master.id),
            agent_id=str(agent.id),
            content=content
        )

        return Response(
            {'message': 'Message queued for sending'},
            status=status.HTTP_200_OK
        )





