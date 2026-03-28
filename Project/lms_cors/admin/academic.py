from django.contrib import admin
from ..models import Institution, Department, Program, AcademicSession, Semester, Subject


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'code', 'city', 'country', 'department_count', 'is_active']
    list_filter = ['is_active', 'country', 'city', 'established_year']
    search_fields = ['name', 'short_name', 'code', 'email', 'city']
    list_editable = ['is_active']
    list_per_page = 20
    
    @admin.display(description='Departments')
    def department_count(self, obj):
        return obj.departments.count()


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
    list_display = ['session_name', 'session_code', 'program', 'status', 'start_year', 'end_year', 'is_active']
    list_filter = ['status', 'is_active', 'program', 'program__department']
    search_fields = ['session_name', 'session_code', 'program__name']
    list_editable = ['status', 'is_active']
    ordering = ['-start_year']
    list_per_page = 20


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
