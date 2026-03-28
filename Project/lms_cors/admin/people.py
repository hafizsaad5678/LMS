from django.contrib import admin
from .base import BaseAdmin
from ..models import Student, Teacher, Admin, TeacherSubject, StudentSubject


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['enrollment_number', 'program', 'enrollment_year', 'current_semester']
    list_filter = BaseAdmin.list_filter + ['program', 'enrollment_year', 'current_semester']
    search_fields = BaseAdmin.search_fields + ['enrollment_number', 'father_name', 'mother_name']


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['employee_id', 'department', 'designation', 'qualification']
    list_filter = BaseAdmin.list_filter + ['department', 'designation', 'joining_date']
    search_fields = BaseAdmin.search_fields + ['employee_id', 'qualification', 'specialization']


@admin.register(Admin)
class AdminAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['admin_id', 'role', 'permissions_level']
    list_filter = BaseAdmin.list_filter + ['role', 'permissions_level']
    search_fields = BaseAdmin.search_fields + ['admin_id', 'role']


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'semester_display', 'program_display']
    list_filter = ['teacher', 'subject__semester', 'subject__semester__program']
    search_fields = ['teacher__full_name', 'subject__name', 'subject__code']
    list_per_page = 20
    
    @admin.display(description='Semester')
    def semester_display(self, obj):
        return obj.subject.semester.name if obj.subject and obj.subject.semester else "N/A"
    
    @admin.display(description='Program')
    def program_display(self, obj):
        if obj.subject and obj.subject.semester and obj.subject.semester.program:
            return obj.subject.semester.program.name
        return "N/A"


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'enrollment_date']
    list_filter = ['semester', 'subject', 'semester__program']
    search_fields = ['student__full_name', 'student__enrollment_number', 'subject__name']
    list_per_page = 20
