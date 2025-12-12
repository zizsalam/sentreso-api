"""
Serializers for Agent model.
"""

from rest_framework import serializers
from apps.agents.models import Agent
from apps.masters.models import Master


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for Agent model."""
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    master_name = serializers.CharField(source='master.name', read_only=True)

    class Meta:
        model = Agent
        fields = (
            'id', 'master_id', 'master_name', 'name', 'whatsapp_number',
            'phone_number', 'risk_score', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'master_id', 'master_name', 'created_at', 'updated_at')
        extra_kwargs = {
            'phone_number': {'required': False, 'allow_blank': True},
        }
