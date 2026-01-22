"""
API views for Master model.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.api.permissions import IsAuthenticatedWithAPIKey
from apps.masters.models import Master
from apps.masters.serializers import MasterCreateSerializer, MasterSerializer


class MasterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Master management.

    - POST /api/v1/masters/ - Register new master (no auth required)
    - GET /api/v1/masters/me/ - Get current master info (authenticated)
    - PATCH /api/v1/masters/me/ - Update current master info (authenticated)
    """
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

    def get_permissions(self):
        """
        Allow registration without auth, but require auth for other actions.
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticatedWithAPIKey()]

    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return MasterCreateSerializer
        return MasterSerializer

    def create(self, request, *args, **kwargs):
        """
        Register a new master.

        Creates a new master and auto-generates an API key.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        master = serializer.save()

        # Return full serializer with API key
        response_serializer = MasterSerializer(master)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Get or update current master information.

        GET /api/v1/masters/me/ - Get current master
        PATCH /api/v1/masters/me/ - Update current master
        """
        # request.auth is set by APIKeyAuthentication to the Master instance
        # Also available as request.master
        master = getattr(request, 'master', request.auth)

        if request.method == 'GET':
            serializer = self.get_serializer(master)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(master, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
