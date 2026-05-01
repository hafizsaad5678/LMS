from django.contrib import admin
from django.utils import timezone
from institution_profile.models import Institution
from ..models import (
    Department, Program,
    AcademicSession, Semester, Subject
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'institution', 'head_of_department', 'program_count', 'teacher_count', 'is_active']
    list_filter = ['institution', 'is_active']
    search_fields = ['name', 'code', 'description', 'head_of_department']
    list_editable = ['is_active']
    list_per_page = 20
    
    @admin.display(description='Programs')
    def program_count(self, obj):
        return obj.programs.count()
    
    @admin.display(description='Teachers')
    def teacher_count(self, obj):
        return obj.teachers.count()


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'duration_years', 'student_count', 'semester_count']
    list_filter = ['department']
    search_fields = ['name', 'code', 'description']
    list_per_page = 20
    
    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.students_legacy.count()
    
    @admin.display(description='Semesters')
    def semester_count(self, obj):
        return obj.semesters_legacy.count()


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_name', 'session_code', 'program', 'status', 'start_year', 'end_year',
        'admission_start_date', 'admission_end_date', 'admissions_open', 'is_active'
    ]
    list_filter = ['status', 'is_active', 'program', 'program__department']
    search_fields = ['session_name', 'session_code', 'program__name']
    list_editable = ['status', 'is_active']
    ordering = ['-start_year']
    list_per_page = 20

    @admin.display(description='Admissions Open', boolean=True)
    def admissions_open(self, obj):
        today = timezone.now().date()
        start_date = obj.admission_start_date
        end_date = obj.admission_end_date

        if start_date and end_date:
            return start_date <= today <= end_date
        if start_date and not end_date:
            return today >= start_date
        if end_date and not start_date:
            return today <= end_date
        return False


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['program', 'number', 'name', 'subject_count']
    list_filter = ['program']
    search_fields = ['name', 'program__name', 'program__code']
    list_per_page = 20
    
    @admin.display(description='Subjects')
    def subject_count(self, obj):
        return obj.subjects.count()


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'semester', 'credit_hours', 'student_count', 'teacher_count']
    list_filter = ['semester', 'semester__program']
    search_fields = ['name', 'code', 'description']
    list_per_page = 20
    
    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.enrolled_students.count()
    
    @admin.display(description='Teachers')
    def teacher_count(self, obj):
        return obj.assigned_teachers.count()
