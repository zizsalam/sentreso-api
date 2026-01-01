"""
Serializers for Reconciliation models.
"""

from rest_framework import serializers
from apps.reconciliation.models import PaymentMatch, ReconciliationRecord
from apps.collections.models import Collection
from apps.agents.models import Agent


class PaymentMatchSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMatch model."""
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    agent_id = serializers.UUIDField(write_only=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    matched_collection_id = serializers.UUIDField(source='matched_collection.id', read_only=True, allow_null=True)

    class Meta:
        model = PaymentMatch
        fields = (
            'id', 'master', 'master_id', 'agent', 'agent_id', 'agent_name',
            'amount', 'transaction_reference', 'payment_method', 'received_at',
            'is_matched', 'matched_collection', 'matched_collection_id',
            'matched_at', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'master', 'master_id', 'agent', 'agent_name',
            'is_matched', 'matched_collection', 'matched_collection_id', 'matched_at',
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
        """Create payment match and set master and agent automatically."""
        master = self.context['request'].master
        agent_id = validated_data.pop('agent_id')
        agent = Agent.objects.get(id=agent_id, master=master)
        validated_data['agent'] = agent
        validated_data['master'] = master
        return super().create(validated_data)


class ReconciliationRecordSerializer(serializers.ModelSerializer):
    """Serializer for ReconciliationRecord model."""
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    agent_id = serializers.UUIDField(source='agent.id', read_only=True, allow_null=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True, allow_null=True)

    class Meta:
        model = ReconciliationRecord
        fields = (
            'id', 'master', 'master_id', 'agent', 'agent_id', 'agent_name',
            'status', 'started_at', 'completed_at', 'total_payments',
            'matched_payments', 'unmatched_payments', 'total_amount',
            'error_message', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'master', 'master_id', 'agent_id', 'agent_name', 'status',
            'started_at', 'completed_at', 'total_payments', 'matched_payments',
            'unmatched_payments', 'total_amount', 'error_message',
            'created_at', 'updated_at'
        )


class StartReconciliationSerializer(serializers.Serializer):
    """Serializer for starting a reconciliation."""
    agent_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_agent_id(self, value):
        """Validate that the agent belongs to the authenticated master if provided."""
        if value:
            master = self.context['request'].master
            try:
                agent = Agent.objects.get(id=value, master=master, is_active=True)
            except Agent.DoesNotExist:
                raise serializers.ValidationError("Agent not found or does not belong to your account.")
        return value

