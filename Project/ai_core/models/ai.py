from django.contrib.auth import get_user_model
from django.db import models
import uuid

User = get_user_model()


class AIUsageLog(models.Model):
    """
    Log every AI request for monitoring and rate limiting
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_logs')
    feature = models.CharField(max_length=50)  # e.g., 'quiz_gen', 'chatbot'
    provider = models.CharField(max_length=50)  # e.g., 'gemini', 'openai'
    model_name = models.CharField(max_length=50)  # e.g., 'gemini-1.5-flash'

    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    status = models.CharField(max_length=20, default='success')  # success, failed
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_usage_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.feature} - {self.created_at}"


class AIPromptTemplate(models.Model):
    """
    Centralized store for AI prompt templates
    """

    name = models.CharField(max_length=50, unique=True)  # e.g., 'QUIZ_GENERATOR'
    template = models.TextField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
