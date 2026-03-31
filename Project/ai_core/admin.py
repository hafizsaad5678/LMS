from django.contrib import admin
from .models import AIUsageLog, AIPromptTemplate, ChatSession, ChatMessage, ChatMetric, UploadedFile


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "feature", "provider", "model_name", "status", "created_at")
	list_filter = ("feature", "provider", "status", "created_at")
	search_fields = ("user__username", "feature", "provider", "model_name", "error_message")
	readonly_fields = ("id", "created_at")


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
	list_display = ("name", "updated_at", "created_at")
	search_fields = ("name", "description")


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "title", "updated_at", "created_at")
	list_filter = ("created_at", "updated_at")
	search_fields = ("user__username", "title")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
	list_display = ("id", "session", "role", "intent", "source", "latency", "confidence", "created_at")
	list_filter = ("role", "intent", "source", "created_at")
	search_fields = ("session__title", "content")


@admin.register(ChatMetric)
class ChatMetricAdmin(admin.ModelAdmin):
	list_display = ("id", "message", "is_grounded", "user_satisfaction", "created_at")
	list_filter = ("is_grounded", "created_at")
	search_fields = ("feedback_text",)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "filename", "index_status", "created_at")
	list_filter = ("index_status", "created_at")
	search_fields = ("filename", "user__username")
