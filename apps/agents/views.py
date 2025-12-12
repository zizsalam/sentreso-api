"""
API views for Agent model.
"""

from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.agents.models import Agent
from apps.agents.serializers import AgentSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Agent management.

    All operations are scoped to the authenticated master.
    """
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'whatsapp_number', 'phone_number']
    ordering_fields = ['created_at', 'name', 'risk_score']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter agents to only those belonging to the authenticated master.
        """
        master = getattr(self.request, 'master', self.request.auth)
        return Agent.objects.get_by_master(master)

    def perform_create(self, serializer):
        """
        Set the master automatically when creating an agent.
        """
        master = getattr(self.request, 'master', self.request.auth)
        serializer.save(master=master)

    def perform_destroy(self, instance):
        """
        Soft delete: set is_active=False instead of actually deleting.
        """
        instance.is_active = False
        instance.save()
