from django.contrib import admin
from django.utils import timezone
from ..models import Event, Holiday, Exam, Timetable


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'event_date', 'created_by', 'days_until']
    list_filter = ['event_type', 'event_date', 'created_by']
    search_fields = ['title', 'description']
    list_per_page = 20
    
    @admin.display(description='Timing')
    def days_until(self, obj):
        delta = obj.event_date - timezone.now().date()
        if delta.days > 0:
            return f"In {delta.days} days"
        elif delta.days == 0:
            return "Today"
        return f"{abs(delta.days)} days ago"


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'holiday_type', 'start_date', 'end_date', 'duration_display', 'is_active']
    list_filter = ['holiday_type', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-start_date']
    list_per_page = 20
    
    @admin.display(description='Duration')
    def duration_display(self, obj):
        days = obj.duration_days
        return f"{days} day{'s' if days > 1 else ''}"


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['subject', 'exam_type', 'exam_date', 'exam_time', 'duration_minutes', 'room', 'status']
    list_filter = ['exam_type', 'status', 'exam_date']
    search_fields = ['subject__name', 'subject__code', 'room']
    list_editable = ['status']
    ordering = ['exam_date', 'exam_time']
    list_per_page = 20


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'subject', 'teacher', 'room', 'program', 'is_active']
    list_filter = ['day', 'is_active', 'program', 'semester']
    search_fields = ['subject__name', 'subject__code', 'teacher__full_name', 'room']
    list_editable = ['is_active']
    ordering = ['day', 'start_time']
    list_per_page = 25
