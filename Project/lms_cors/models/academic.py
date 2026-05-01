from django.db import models
import uuid
from institution_profile.models import Institution


def generate_sequential_id(model_class, field_name, prefix, filter_field=None, filter_value=None):
    """
    Utility function to generate sequential IDs.
    Reduces code duplication across Student, Teacher, Admin models.
    """
    qs = model_class.objects.all()
    if filter_field and filter_value:
        qs = qs.filter(**{filter_field: filter_value})
    
    last = qs.order_by('-created_at').first()
    new_num = 1
    
    if last:
        last_id = getattr(last, field_name, None)
        if last_id:
            try:
                parts = last_id.split('-')
                new_num = int(parts[-1]) + 1
            except (ValueError, IndexError):
                pass
    
    suffix = f"-{new_num:04d}"

    # Keep generated IDs within the model field limit (e.g., Teacher.employee_id max_length=20).
    field = model_class._meta.get_field(field_name)
    max_length = getattr(field, 'max_length', None)

    if max_length:
        allowed_prefix_len = max_length - len(suffix)
        if allowed_prefix_len < 1:
            # Defensive fallback for unusually small max_length values.
            return suffix[-max_length:]

        prefix = str(prefix)[:allowed_prefix_len].rstrip('-')
        if not prefix:
            prefix = str(model_class.__name__).upper()[:allowed_prefix_len]

    return f"{prefix}{suffix}"



class Department(models.Model):
    """Department model for academic departments - belongs to an Institution"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='departments',
        null=True, 
        blank=True,
        help_text="The institution this department belongs to"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    head_of_department = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='department_images/', blank=True, null=True)
    description = models.TextField(blank=True)
    vision = models.TextField(blank=True, help_text="Department's future goals and vision")
    mission = models.TextField(blank=True, help_text="Department's core mission and purpose")
    academic_focus = models.TextField(blank=True, help_text="Main research or academic areas")
    facilities = models.TextField(blank=True, help_text="Labs, libraries, and other facilities")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        if self.institution:
            return f"{self.name} ({self.code}) - {self.institution.short_name or self.institution.code}"
        return f"{self.name} ({self.code})"


class Program(models.Model):
    """Academic Program model"""
    PROGRAM_LEVEL_CHOICES = [
        ('bachelor', 'Bachelor (BS)'),
        ('master', 'Master (MS/MPhil)'),
        ('phd', 'Doctorate (PhD)'),
        ('intermediate', 'Intermediate (FSc/FA)'),
        ('diploma', 'Diploma/Certificate'),
    ]
    
    ACADEMIC_SYSTEM_CHOICES = [
        ('semester', 'Semester System'),
        ('annual', 'Annual System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, 
        related_name='programs', null=True, blank=True
    )
    duration_years = models.IntegerField(default=4)
    program_level = models.CharField(
        max_length=20, 
        choices=PROGRAM_LEVEL_CHOICES,
        default='bachelor'
    )
    academic_system = models.CharField(
        max_length=20,
        choices=ACADEMIC_SYSTEM_CHOICES,
        default='semester'
    )
    default_semesters = models.IntegerField(default=8)
    min_credit_hours = models.IntegerField(default=130)
    max_credit_hours = models.IntegerField(default=140)
    requires_thesis = models.BooleanField(default=False)
    requires_internship = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    
    def __str__(self):
        return f"{self.name} - {self.department.name}" if self.department else self.name


class AcademicSession(models.Model):
    """
    Academic Session (Batch/Intake) model.
    Represents a specific intake period (e.g., Fall 2024, Spring 2025).
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE,
        related_name='sessions', null=True, blank=True
    )
    session_name = models.CharField(max_length=100)
    session_code = models.CharField(max_length=50, unique=True, help_text="Unique code e.g., CS-2024-F")
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_active = models.BooleanField(default=True)
    total_capacity = models.IntegerField(default=60, help_text="Maximum students allowed in this session")
    description = models.TextField(blank=True)
    edit_count = models.IntegerField(default=0)
    
    # Admission dates
    admission_start_date = models.DateField(null=True, blank=True, help_text="When admissions open")
    admission_end_date = models.DateField(null=True, blank=True, help_text="When admissions close")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_year', 'program']
        db_table = 'academic_sessions'
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'

    def __str__(self):
        return f"{self.session_name} ({self.session_code})"
    
    @property
    def total_semesters(self):
        return self.semesters.count()
    
    @property
    def current_enrollment(self):
        """Get current number of enrolled students"""
        return self.students.count()
    
    @property
    def is_full(self):
        """Check if session has reached capacity"""
        return self.current_enrollment >= self.total_capacity
    
    @property
    def available_seats(self):
        """Get number of available seats"""
        return max(0, self.total_capacity - self.current_enrollment)


class Semester(models.Model):
    """Semester model within a Program"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, 
        related_name='semesters_legacy', null=True, blank=True
    )
    session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE,
        related_name='semesters', null=True, blank=True
    )
    number = models.IntegerField()
    name = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['session', 'number']
        unique_together = ['session', 'number']
    
    def __str__(self):
        if self.program:
            return f"{self.program.name} - Semester {self.number}"
        return f"Semester {self.number}: {self.name}"


class Subject(models.Model):
    """Subject model within a Semester"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, 
        related_name='subjects', null=True, blank=True
    )
    description = models.TextField(blank=True)
    credit_hours = models.IntegerField(default=3)
    
    class Meta:
        ordering = ['code', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
