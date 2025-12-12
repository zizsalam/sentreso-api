"""
Serializers for Master model.
"""

from rest_framework import serializers
from apps.masters.models import Master


class MasterCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new master (registration)."""

    class Meta:
        model = Master
        fields = ('name', 'email', 'webhook_url')
        extra_kwargs = {
            'webhook_url': {'required': False, 'allow_blank': True},
        }


class MasterSerializer(serializers.ModelSerializer):
    """Serializer for reading/updating master information."""

    class Meta:
        model = Master
        fields = ('id', 'name', 'email', 'api_key', 'webhook_url', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'api_key', 'created_at', 'updated_at')
        extra_kwargs = {
            'webhook_url': {'required': False, 'allow_blank': True},
        }
