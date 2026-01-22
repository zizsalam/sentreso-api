"""
Serializers for Collection model.
"""

from rest_framework import serializers
from apps.collections.models import Collection
from apps.agents.models import Agent


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for Collection model."""
    agent_id = serializers.UUIDField(write_only=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    agent_whatsapp = serializers.CharField(source='agent.whatsapp_number', read_only=True)
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    master_name = serializers.CharField(source='master.name', read_only=True)

    class Meta:
        model = Collection
        fields = (
            'id', 'agent', 'agent_id', 'agent_name', 'agent_whatsapp',
            'master', 'master_id', 'master_name', 'amount', 'status',
            'payment_method', 'transaction_reference', 'due_date', 'paid_at',
            'notes', 'last_reminder_sent', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'agent_name', 'agent_whatsapp', 'master', 'master_id',
            'master_name', 'status', 'paid_at', 'last_reminder_sent',
            'created_at', 'updated_at'
        )

    def validate_agent_id(self, value):
        """Validate that the agent belongs to the authenticated master."""
        master = self.context['request'].master
        try:
            agent = Agent.objects.get(id=value, master=master, is_active=True)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent not found or does not belong to your account.")
        return value

    def create(self, validated_data):
        """Create a collection and set the master automatically."""
        agent_id = validated_data.pop('agent_id')
        master = self.context['request'].master
        agent = Agent.objects.get(id=agent_id, master=master)
        validated_data['agent'] = agent
        validated_data['master'] = master
        return super().create(validated_data)


class CollectionMarkPaidSerializer(serializers.Serializer):
    """Serializer for marking a collection as paid."""
    transaction_reference = serializers.CharField(max_length=255, required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=Collection.PAYMENT_METHOD_CHOICES, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)








