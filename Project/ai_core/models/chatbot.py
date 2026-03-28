from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10) # 'user' or 'bot'
    content = models.TextField()
    intent = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    latency = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

class ChatMetric(models.Model):
    """
    Stores evaluation metrics for each interaction
    """
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='metrics')
    is_grounded = models.BooleanField(default=True) # Factual correctness check
    user_satisfaction = models.IntegerField(null=True, blank=True) # 1-5 rating
    feedback_text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_metrics'

class UploadedFile(models.Model):
    """
    Specifically for chatbot document Q&A if separate from general LMS materials.
    Or we can just store references to lms_cors.Material.
    Let's use references for the MVP.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey('lms_cors.Material', on_delete=models.CASCADE, null=True, blank=True)
    filename = models.CharField(max_length=255)
    index_status = models.CharField(max_length=20, default='pending') # pending, indexed, failed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_uploaded_files'

class FileChunk(models.Model):
    """
    Metadata for searchable chunks if we need DB tracking beyond FAISS meta.
    """
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content_summary = models.TextField() # For quick preview
    
    class Meta:
        db_table = 'chat_file_chunks'
