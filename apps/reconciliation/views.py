"""
API views for Reconciliation models.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.api.permissions import IsAuthenticatedWithAPIKey
from django.utils import timezone
from apps.reconciliation.models import PaymentMatch, ReconciliationRecord
from apps.reconciliation.serializers import (
    PaymentMatchSerializer,
    ReconciliationRecordSerializer,
    StartReconciliationSerializer
)
from apps.reconciliation.services import ReconciliationService
from apps.agents.models import Agent


class PaymentMatchViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentMatch management."""
    serializer_class = PaymentMatchSerializer
    permission_classes = [IsAuthenticatedWithAPIKey]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['transaction_reference', 'notes']
    ordering_fields = ['created_at', 'received_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter payments to only those belonging to the authenticated master."""
        master = getattr(self.request, 'master', self.request.auth)
        queryset = PaymentMatch.objects.filter(master=master)

        # Filter by is_matched
        is_matched = self.request.query_params.get('is_matched', None)
        if is_matched is not None:
            is_matched = is_matched.lower() == 'true'
            queryset = queryset.filter(is_matched=is_matched)

        # Filter by agent_id
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        return queryset


class ReconciliationRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing ReconciliationRecord (read-only)."""
    serializer_class = ReconciliationRecordSerializer
    permission_classes = [IsAuthenticatedWithAPIKey]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'started_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter records to only those belonging to the authenticated master."""
        master = getattr(self.request, 'master', self.request.auth)
        queryset = ReconciliationRecord.objects.filter(master=master)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by agent_id
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        return queryset

    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a reconciliation process.

        POST /api/v1/reconciliation/records/start/
        """
        serializer = StartReconciliationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        master = request.master
        agent_id = serializer.validated_data.get('agent_id')
        agent = None

        if agent_id:
            agent = Agent.objects.get(id=agent_id, master=master)

        # Run reconciliation
        service = ReconciliationService()
        record = service.reconcile(master, agent=agent)

        response_serializer = ReconciliationRecordSerializer(record)
        return Response(response_serializer.data, status=status.HTTP_200_OK)





