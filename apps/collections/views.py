"""
API views for Collection model.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from apps.collections.models import Collection
from apps.collections.serializers import CollectionSerializer, CollectionMarkPaidSerializer
from apps.core.webhooks import send_webhook


class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Collection management.

    All operations are scoped to the authenticated master.
    """
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['agent__name', 'agent__whatsapp_number', 'transaction_reference', 'notes']
    ordering_fields = ['created_at', 'due_date', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter collections to only those belonging to the authenticated master."""
        master = getattr(self.request, 'master', self.request.auth)
        queryset = Collection.objects.filter(master=master)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by agent_id
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """Create collection and send webhook."""
        collection = serializer.save()

        # Send webhook notification
        send_webhook(
            master=collection.master,
            event='collection.created',
            data={
                'id': str(collection.id),
                'agent_name': collection.agent.name,
                'amount': str(collection.amount),
                'status': collection.status,
                'due_date': collection.due_date.isoformat() if collection.due_date else None,
            }
        )

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark a collection as paid.

        POST /api/v1/collections/{id}/mark_paid/
        """
        collection = self.get_object()
        if collection.status != 'pending':
            return Response(
                {'error': f'Collection is already {collection.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CollectionMarkPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        collection.mark_as_paid(
            transaction_reference=serializer.validated_data.get('transaction_reference'),
            payment_method=serializer.validated_data.get('payment_method'),
            notes=serializer.validated_data.get('notes')
        )

        # Send webhook notification
        send_webhook(
            master=collection.master,
            event='collection.paid',
            data={
                'collection_id': str(collection.id),
                'agent_name': collection.agent.name,
                'amount': str(collection.amount),
                'status': collection.status,
                'transaction_reference': collection.transaction_reference,
                'payment_method': collection.payment_method,
                'paid_at': collection.paid_at.isoformat() if collection.paid_at else None,
            }
        )

        response_serializer = CollectionSerializer(collection)
        return Response(response_serializer.data)

