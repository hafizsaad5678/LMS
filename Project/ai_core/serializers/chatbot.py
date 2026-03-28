from rest_framework import serializers
from ..models.chatbot import ChatSession, ChatMessage, ChatMetric

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'intent', 'source', 'latency', 'confidence', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'messages', 'created_at', 'updated_at']

class ChatMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMetric
        fields = ['id', 'message', 'is_grounded', 'user_satisfaction', 'feedback_text']
