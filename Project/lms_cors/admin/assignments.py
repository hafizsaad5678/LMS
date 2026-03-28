from django.contrib import admin
from ..models import Assignment, SubmissionHistory, Grade


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date', 'created_by', 'total_marks', 'submission_count']
    list_filter = ['subject', 'created_by', 'due_date', 'subject__semester']
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    list_per_page = 20
    
    @admin.display(description='Submissions')
    def submission_count(self, obj):
        return obj.submissions.count()


@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'has_grade', 'grade_value']
    list_filter = ['assignment', 'assignment__subject', 'submitted_at']
    search_fields = ['student__full_name', 'student__enrollment_number', 'assignment__title']
    list_per_page = 20
    
    @admin.display(boolean=True, description='Graded')
    def has_grade(self, obj):
        return hasattr(obj, 'grade') and obj.grade is not None
    
    @admin.display(description='Grade')
    def grade_value(self, obj):
        try:
            return obj.grade.grade_value
        except (Grade.DoesNotExist, AttributeError):
            return "No Grade"


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['submission', 'grade_value', 'marks_obtained', 'graded_by', 'graded_at']
    list_filter = ['grade_value', 'graded_by', 'graded_at', 'submission__assignment__subject']
    search_fields = ['submission__student__full_name', 'submission__assignment__title']
    list_per_page = 20
