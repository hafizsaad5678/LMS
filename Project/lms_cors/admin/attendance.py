from django.contrib import admin
from ..models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'session_date', 'status', 'marked_by', 'marked_at']
    list_filter = ['subject', 'status', 'session_date', 'marked_by', 'subject__semester']
    search_fields = ['student__full_name', 'student__enrollment_number', 'subject__name']
    list_per_page = 20
