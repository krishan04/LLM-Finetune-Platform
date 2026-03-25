from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "token_count", "created_at"]
        read_only_fields = ["id", "token_count", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "summary", "message_count", "created_at", "last_active_at"]
        read_only_fields = ["id", "summary", "message_count", "created_at", "last_active_at"]