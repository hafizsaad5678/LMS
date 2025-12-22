from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Institution, Department, Program, AcademicSession, Semester, Subject,
    Student, Teacher, TeacherSubject, StudentSubject,
    Assignment, SubmissionHistory, Grade, Attendance,
    Admin, Event, Holiday, Exam, Timetable,
    Fee, Expense, Account, LibraryBook, BookBorrowing
)


class BaseAdmin(admin.ModelAdmin):
    """Base admin class for profile-based models"""
    list_display = ['get_identifier', 'full_name', 'email', 'phone', 'profile_status_display', 'is_active']
    list_filter = ['is_active', 'is_verified', 'is_suspended', 'gender', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'cnic']
    readonly_fields = ['created_at', 'updated_at', 'age_display', 'profile_status_display', 
                      'verified_at', 'suspended_at', 'last_login_at', 'edit_count', 'profile_image_display']
    list_editable = ['is_active']
    list_per_page = 20
    actions = ['activate_selected', 'deactivate_selected', 'verify_selected', 'suspend_selected']
    
    fieldsets = (
        ('Identification', {
            'fields': ('full_name', 'email', 'phone', 'gender', 'cnic')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'blood_group', 'nationality', 'age_display')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'postal_code', 
                      'emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('Profile Media', {
            'fields': ('profile_image_display', 'profile_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_suspended', 'profile_status_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at', 'suspended_at', 'last_login_at'),
            'classes': ('collapse',)
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='Age')
    def age_display(self, obj):
        return getattr(obj, 'age_display', 'N/A')
    
    @admin.display(description='Status')
    def profile_status_display(self, obj):
        status = getattr(obj, 'profile_status', 'Unknown')
        colors = {'Verified': 'green', 'Active': 'blue', 'Inactive': 'orange', 
                  'Suspended': 'red', 'Pending': 'gray'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          colors.get(status, 'black'), status)
    
    @admin.display(description='Profile Image')
    def profile_image_display(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;" />', 
                             obj.profile_image.url)
        return "No Image"
    
    @admin.display(description='ID')
    def get_identifier(self, obj):
        for attr in ['enrollment_number', 'employee_id', 'admin_id']:
            if hasattr(obj, attr):
                return getattr(obj, attr)
        return str(obj.id)[:8]
    
    @admin.action(description="Activate selected profiles")
    def activate_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.activate()
            count += 1
        self.message_user(request, f"{count} profiles activated.")
    
    @admin.action(description="Deactivate selected profiles")
    def deactivate_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.deactivate()
            count += 1
        self.message_user(request, f"{count} profiles deactivated.")
    
    @admin.action(description="Verify selected profiles")
    def verify_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.verify()
            count += 1
        self.message_user(request, f"{count} profiles verified.")
    
    @admin.action(description="Suspend selected profiles")
    def suspend_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.suspend("Bulk suspension from admin")
            count += 1
        self.message_user(request, f"{count} profiles suspended.")


# ==================== PEOPLE ADMIN ====================

@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['enrollment_number', 'program', 'enrollment_year', 'current_semester']
    list_filter = BaseAdmin.list_filter + ['program', 'enrollment_year', 'current_semester']
    search_fields = BaseAdmin.search_fields + ['enrollment_number', 'father_name', 'mother_name']
    
    fieldsets = (
        ('Identification', {
            'fields': ('enrollment_number', 'full_name', 'email', 'phone', 'gender', 'cnic')
        }),
        ('Academic Details', {
            'fields': ('program', 'enrollment_year', 'current_semester', 'previous_education')
        }),
        ('Family Details', {
            'fields': ('father_name', 'mother_name', 'guardian_phone'),
            'classes': ('collapse',)
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'blood_group', 'nationality', 'age_display')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'postal_code', 
                      'emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('Profile Media', {
            'fields': ('profile_image_display', 'profile_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_suspended', 'profile_status_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at', 'suspended_at', 'last_login_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['employee_id', 'department', 'designation', 'qualification']
    list_filter = BaseAdmin.list_filter + ['department', 'designation', 'joining_date']
    search_fields = BaseAdmin.search_fields + ['employee_id', 'qualification', 'specialization']
    
    fieldsets = (
        ('Identification', {
            'fields': ('employee_id', 'full_name', 'email', 'phone', 'gender', 'cnic')
        }),
        ('Professional Details', {
            'fields': ('department', 'qualification', 'designation', 
                      'specialization', 'experience_years', 'joining_date')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'blood_group', 'nationality', 'age_display')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'postal_code', 
                      'emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('Profile Media', {
            'fields': ('profile_image_display', 'profile_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_suspended', 'profile_status_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at', 'suspended_at', 'last_login_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Admin)
class AdminAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ['admin_id', 'role', 'permissions_level']
    list_filter = BaseAdmin.list_filter + ['role', 'permissions_level']
    search_fields = BaseAdmin.search_fields + ['admin_id', 'role']
    
    fieldsets = (
        ('Identification', {
            'fields': ('admin_id', 'full_name', 'email', 'phone', 'gender', 'cnic', 'role', 'permissions_level')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'blood_group', 'nationality', 'age_display')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'postal_code', 
                      'emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('Profile Media', {
            'fields': ('profile_image_display', 'profile_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_suspended', 'profile_status_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at', 'suspended_at', 'last_login_at'),
            'classes': ('collapse',)
        })
    )


# ==================== ACADEMIC STRUCTURE ADMIN ====================

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """Admin configuration for Institution model"""
    list_display = ['name', 'short_name', 'code', 'city', 'country', 'department_count', 'is_active']
    list_filter = ['is_active', 'country', 'city', 'established_year']
    search_fields = ['name', 'short_name', 'code', 'email', 'city']
    list_editable = ['is_active']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at', 'logo_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'code', 'established_year')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Branding', {
            'fields': ('logo_preview', 'logo', 'description'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Departments')
    def department_count(self, obj):
        return obj.departments.count()
    
    @admin.display(description='Logo Preview')
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="150" height="auto" style="border-radius: 8px;" />', obj.logo.url)
        return "No Logo"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'institution', 'head_of_department', 'program_count', 'teacher_count', 'is_active']
    list_filter = ['institution', 'is_active']
    search_fields = ['name', 'code', 'description', 'head_of_department']
    list_editable = ['is_active']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['institution']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('institution', 'name', 'code', 'head_of_department')
        }),
        ('Contact', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    autocomplete_fields = ['program']
    
    fieldsets = (
        ('Session Details', {
            'fields': ('session_name', 'session_code', 'program', 'description')
        }),
        ('Timeline', {
            'fields': ('start_year', 'end_year')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
    )


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


# ==================== JUNCTION TABLES ADMIN ====================

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'semester_display', 'program_display']
    list_filter = ['teacher', 'subject__semester', 'subject__semester__program']
    search_fields = ['teacher__full_name', 'subject__name', 'subject__code']
    list_per_page = 20
    autocomplete_fields = ['teacher', 'subject']
    
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
    list_display = ['student', 'subject', 'semester', 'enrollment_date', 'program_display']
    list_filter = ['semester', 'subject', 'semester__program']
    search_fields = ['student__full_name', 'student__enrollment_number', 'subject__name']
    list_per_page = 20
    autocomplete_fields = ['student', 'subject', 'semester']
    
    @admin.display(description='Program')
    def program_display(self, obj):
        return obj.semester.program.name if obj.semester and obj.semester.program else "N/A"


# ==================== ACADEMIC MANAGEMENT ADMIN ====================

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date', 'created_by', 'total_marks', 'submission_count']
    list_filter = ['subject', 'created_by', 'due_date', 'subject__semester']
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['subject', 'created_by']
    
    @admin.display(description='Submissions')
    def submission_count(self, obj):
        return obj.submissions.count()


@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'has_grade', 'grade_value']
    list_filter = ['assignment', 'assignment__subject', 'submitted_at']
    search_fields = ['student__full_name', 'student__enrollment_number', 'assignment__title']
    list_per_page = 20
    readonly_fields = ['submitted_at']
    autocomplete_fields = ['assignment', 'student']
    
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
    readonly_fields = ['graded_at']
    autocomplete_fields = ['submission', 'graded_by']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'session_date', 'status', 'marked_by', 'marked_at']
    list_filter = ['subject', 'status', 'session_date', 'marked_by', 'subject__semester']
    search_fields = ['student__full_name', 'student__enrollment_number', 'subject__name']
    list_per_page = 20
    readonly_fields = ['marked_at']
    autocomplete_fields = ['subject', 'student', 'marked_by']


# ==================== ADMINISTRATION ADMIN ====================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'event_date', 'created_by', 'days_until']
    list_filter = ['event_type', 'event_date', 'created_by']
    search_fields = ['title', 'description']
    list_per_page = 20
    readonly_fields = ['created_at']
    autocomplete_fields = ['created_by']
    
    @admin.display(description='Timing')
    def days_until(self, obj):
        delta = obj.event_date - timezone.now().date()
        if delta.days > 0:
            return f"In {delta.days} days"
        elif delta.days == 0:
            return "Today"
        return f"{abs(delta.days)} days ago"


# ==================== INLINE ADMIN CLASSES ====================

class TeacherSubjectInline(admin.TabularInline):
    model = TeacherSubject
    extra = 1
    autocomplete_fields = ['subject']


class StudentSubjectInline(admin.TabularInline):
    model = StudentSubject
    extra = 1
    autocomplete_fields = ['subject', 'semester']


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1
    readonly_fields = ['created_at']
    fields = ['title', 'due_date', 'total_marks', 'created_at']


class SubmissionHistoryInline(admin.TabularInline):
    model = SubmissionHistory
    extra = 0
    readonly_fields = ['submitted_at']
    fields = ['assignment', 'submitted_at', 'file_upload']


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ['marked_at']
    fields = ['student', 'session_date', 'status', 'marked_at']


# Add inlines to admin classes
TeacherAdmin.inlines = [TeacherSubjectInline]
StudentAdmin.inlines = [StudentSubjectInline, SubmissionHistoryInline]
SubjectAdmin.inlines = [AssignmentInline, TeacherSubjectInline, StudentSubjectInline]


# ==================== ACADEMIC SCHEDULING ADMIN ====================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'holiday_type', 'start_date', 'end_date', 'duration_display', 'is_active']
    list_filter = ['holiday_type', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-start_date']
    list_per_page = 20
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Holiday Information', {
            'fields': ('name', 'description', 'holiday_type')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
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
    date_hierarchy = 'exam_date'
    autocomplete_fields = ['subject']
    
    fieldsets = (
        ('Exam Information', {
            'fields': ('subject', 'exam_type', 'total_marks')
        }),
        ('Schedule', {
            'fields': ('exam_date', 'exam_time', 'duration_minutes', 'room')
        }),
        ('Status & Instructions', {
            'fields': ('status', 'instructions')
        }),
    )


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'subject', 'teacher', 'room', 'program', 'is_active']
    list_filter = ['day', 'is_active', 'program', 'semester']
    search_fields = ['subject__name', 'subject__code', 'teacher__full_name', 'room']
    list_editable = ['is_active']
    ordering = ['day', 'start_time']
    list_per_page = 25
    autocomplete_fields = ['subject', 'teacher', 'program', 'semester']
    
    fieldsets = (
        ('Schedule', {
            'fields': ('day', 'start_time', 'end_time', 'room')
        }),
        ('Class Details', {
            'fields': ('subject', 'teacher', 'program', 'semester')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


# ==================== MANAGEMENT/FINANCIAL ADMIN ====================

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_type', 'amount', 'paid_amount', 'balance_display', 'due_date', 'status']
    list_filter = ['fee_type', 'status', 'due_date', 'semester']
    search_fields = ['student__full_name', 'student__enrollment_number', 'receipt_number']
    list_editable = ['status']
    ordering = ['-due_date']
    list_per_page = 20
    date_hierarchy = 'due_date'
    autocomplete_fields = ['student', 'semester']
    actions = ['mark_as_paid']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'semester')
        }),
        ('Fee Details', {
            'fields': ('fee_type', 'amount', 'paid_amount', 'receipt_number')
        }),
        ('Payment Information', {
            'fields': ('due_date', 'payment_date', 'status')
        }),
        ('Notes', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Balance')
    def balance_display(self, obj):
        balance = obj.balance
        color = 'red' if balance > 0 else 'green'
        return format_html('<span style="color: {};">PKR {}</span>', color, balance)
    
    @admin.action(description="Mark selected fees as paid")
    def mark_as_paid(self, request, queryset):
        count = queryset.update(status='paid', payment_date=timezone.now().date())
        for fee in queryset:
            fee.paid_amount = fee.amount
            fee.save()
        self.message_user(request, f"{count} fees marked as paid.")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount_display', 'expense_date', 'vendor', 'department', 'is_approved']
    list_filter = ['category', 'is_approved', 'expense_date', 'department']
    search_fields = ['title', 'description', 'vendor', 'receipt_number']
    list_editable = ['is_approved']
    ordering = ['-expense_date']
    list_per_page = 20
    date_hierarchy = 'expense_date'
    autocomplete_fields = ['approved_by', 'department']
    actions = ['approve_expenses']
    
    fieldsets = (
        ('Expense Details', {
            'fields': ('title', 'description', 'category', 'amount')
        }),
        ('Date & Vendor', {
            'fields': ('expense_date', 'vendor', 'receipt_number')
        }),
        ('Department & Approval', {
            'fields': ('department', 'is_approved', 'approved_by')
        }),
    )
    
    @admin.display(description='Amount')
    def amount_display(self, obj):
        return format_html('<strong>PKR {}</strong>', obj.amount)
    
    @admin.action(description="Approve selected expenses")
    def approve_expenses(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} expenses approved.")





@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'account_number', 'bank_name', 'balance_display', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['name', 'account_number', 'bank_name']
    list_editable = ['is_active']
    ordering = ['name']
    list_per_page = 20
    
    fieldsets = (
        ('Account Information', {
            'fields': ('name', 'account_type', 'description')
        }),
        ('Bank Details', {
            'fields': ('account_number', 'bank_name')
        }),
        ('Balance & Status', {
            'fields': ('balance', 'is_active')
        }),
    )
    
    @admin.display(description='Balance')
    def balance_display(self, obj):
        return format_html('<strong style="color: green;">PKR {}</strong>', obj.balance)


# ==================== LIBRARY ADMIN ====================

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'copies_total', 'copies_available', 'status']
    list_filter = ['status', 'category', 'publication_year']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    list_editable = ['status']
    ordering = ['title']
    list_per_page = 25
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'publisher', 'publication_year')
        }),
        ('Classification', {
            'fields': ('category', 'location')
        }),
        ('Inventory', {
            'fields': ('copies_total', 'copies_available', 'status')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BookBorrowing)
class BookBorrowingAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower_display', 'borrowed_date', 'due_date', 'returned_date', 'status', 'fine_display']
    list_filter = ['status', 'borrowed_date', 'due_date']
    search_fields = ['book__title', 'student__full_name', 'teacher__full_name']
    list_editable = ['status']
    ordering = ['-borrowed_date']
    list_per_page = 20
    autocomplete_fields = ['book', 'student', 'teacher']
    actions = ['mark_as_returned']
    
    fieldsets = (
        ('Book', {
            'fields': ('book',)
        }),
        ('Borrower', {
            'fields': ('student', 'teacher'),
            'description': 'Select either student OR teacher'
        }),
        ('Dates', {
            'fields': ('due_date', 'returned_date')
        }),
        ('Status & Fine', {
            'fields': ('status', 'fine_amount')
        }),
    )
    
    @admin.display(description='Borrower')
    def borrower_display(self, obj):
        if obj.student:
            return f"Student: {obj.student.full_name}"
        elif obj.teacher:
            return f"Teacher: {obj.teacher.full_name}"
        return "Unknown"
    
    @admin.display(description='Fine')
    def fine_display(self, obj):
        if obj.fine_amount > 0:
            return format_html('<span style="color: red;">PKR {}</span>', obj.fine_amount)
        return "-"
    
    @admin.action(description="Mark selected as returned")
    def mark_as_returned(self, request, queryset):
        count = 0
        for borrowing in queryset:
            borrowing.status = 'returned'
            borrowing.returned_date = timezone.now().date()
            borrowing.book.copies_available += 1
            borrowing.book.save()
            borrowing.save()
            count += 1
        self.message_user(request, f"{count} books marked as returned.")