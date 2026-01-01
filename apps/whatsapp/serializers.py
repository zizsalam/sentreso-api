"""
Serializers for WhatsApp models.
"""

from rest_framework import serializers
from apps.whatsapp.models import WhatsAppTemplate, WhatsAppMessage
from apps.collections.models import Collection


class WhatsAppTemplateSerializer(serializers.ModelSerializer):
    """Serializer for WhatsAppTemplate model."""
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    master_name = serializers.CharField(source='master.name', read_only=True)

    class Meta:
        model = WhatsAppTemplate
        fields = (
            'id', 'master', 'master_id', 'master_name', 'name',
            'whatsapp_template_name', 'template_type', 'content', 'variables',
            'language_code', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'master', 'master_id', 'master_name', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Create template and set master automatically."""
        master = self.context['request'].master
        validated_data['master'] = master
        return super().create(validated_data)


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    """Serializer for WhatsAppMessage model."""
    master_id = serializers.UUIDField(source='master.id', read_only=True)
    master_name = serializers.CharField(source='master.name', read_only=True)
    agent_id = serializers.UUIDField(source='agent.id', read_only=True, allow_null=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True, allow_null=True)
    agent_whatsapp = serializers.CharField(source='agent.whatsapp_number', read_only=True, allow_null=True)
    collection_id = serializers.UUIDField(source='collection.id', read_only=True, allow_null=True)
    template_id = serializers.UUIDField(source='template.id', read_only=True, allow_null=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)

    class Meta:
        model = WhatsAppMessage
        fields = (
            'id', 'master', 'master_id', 'master_name', 'agent', 'agent_id',
            'agent_name', 'agent_whatsapp', 'collection', 'collection_id',
            'template', 'template_id', 'template_name', 'direction', 'status',
            'to_number', 'from_number', 'message_id', 'content', 'sent_at',
            'delivered_at', 'read_at', 'received_at', 'error_message',
            'metadata', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'master', 'master_id', 'master_name', 'agent_id',
            'agent_name', 'agent_whatsapp', 'collection_id', 'template_id',
            'template_name', 'status', 'message_id', 'sent_at', 'delivered_at',
            'read_at', 'received_at', 'error_message', 'created_at', 'updated_at'
        )


class SendReminderSerializer(serializers.Serializer):
    """Serializer for sending a collection reminder."""
    collection_id = serializers.UUIDField()

    def validate_collection_id(self, value):
        """Validate that the collection belongs to the authenticated master."""
        master = self.context['request'].master
        try:
            collection = Collection.objects.get(id=value, master=master)
        except Collection.DoesNotExist:
            raise serializers.ValidationError("Collection not found or does not belong to your account.")
        return value


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a custom message."""
    agent_id = serializers.UUIDField()
    content = serializers.CharField()

    def validate_agent_id(self, value):
        """Validate that the agent belongs to the authenticated master."""
        master = self.context['request'].master
        try:
            agent = master.agents.get(id=value, is_active=True)
        except:
            raise serializers.ValidationError("Agent not found or does not belong to your account.")
        return value

