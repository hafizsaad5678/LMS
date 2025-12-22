from django.db import models
from django.core.exceptions import ValidationError
from .base_models import BaseProfile
import uuid


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
    
    return f"{prefix}-{new_num:04d}"


# ==================== CORE ACADEMIC STRUCTURE ====================

class Institution(models.Model):
    """
    Institution model - The top-level entity representing a college/university.
    All departments belong to an institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300, help_text="Full name of the institution")
    short_name = models.CharField(max_length=50, blank=True, help_text="Abbreviation e.g., MIT, NUST")
    code = models.CharField(max_length=20, unique=True, help_text="Unique institution code")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    # Address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Pakistan')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional Info
    established_year = models.IntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'institutions'
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


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
    description = models.TextField(blank=True)
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
        choices=[
            ('bachelor', 'Bachelor (BS)'),
            ('master', 'Master (MS/MPhil)'),
            ('phd', 'Doctorate (PhD)'),
            ('intermediate', 'Intermediate (FSc/FA)'),
            ('diploma', 'Diploma/Certificate'),
        ],
        default='bachelor'
    )
    academic_system = models.CharField(
        max_length=20,
        choices=[
            ('semester', 'Semester System'),
            ('annual', 'Annual System'),
        ],
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
        ordering = ['program', 'number']
        unique_together = ['program', 'number']
    
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


# ==================== PEOPLE MODELS ====================

class Student(BaseProfile):
    """Student model extending BaseProfile"""
    enrollment_number = models.CharField(max_length=20, unique=True, blank=True)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, 
        related_name='students_legacy', null=True, blank=True
    )
    session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE,
        related_name='students', null=True, blank=True
    )
    enrollment_year = models.IntegerField(default=2024)
    current_semester = models.IntegerField(default=1)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    previous_education = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.enrollment_number:
            year_code = str(self.enrollment_year)[-2:]
            program_code = self.program.code if self.program else "GEN"
            self.enrollment_number = generate_sequential_id(
                Student, 'enrollment_number', 
                f"{program_code}-{year_code}",
                'program', self.program
            )
        
        if not self.user:
            self.create_user_account()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.enrollment_number})"


class Teacher(BaseProfile):
    """Teacher model extending BaseProfile"""
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, 
        related_name='teachers', null=True, blank=True
    )
    qualification = models.CharField(max_length=200, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'teachers'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            dept_code = self.department.code if self.department else "GEN"
            self.employee_id = generate_sequential_id(
                Teacher, 'employee_id',
                f"{dept_code}-TCH",
                'department', self.department
            )
        
        if not self.user:
            self.create_user_account()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


class Admin(BaseProfile):
    """Admin model extending BaseProfile"""
    PERMISSION_CHOICES = [
        ('super', 'Super Admin'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]
    
    admin_id = models.CharField(max_length=20, unique=True, blank=True)
    role = models.CharField(max_length=50, default='Administrator')
    permissions_level = models.CharField(
        max_length=20, choices=PERMISSION_CHOICES, default='admin'
    )
    
    class Meta:
        db_table = 'admins'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.admin_id:
            self.admin_id = generate_sequential_id(Admin, 'admin_id', "ADM")
        
        if not self.user:
            self.create_user_account()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.admin_id})"


# ==================== JUNCTION TABLES ====================

class TeacherSubject(models.Model):
    """Many-to-Many relationship between Teacher and Subject"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='teaching_subjects', null=True, blank=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='assigned_teachers', null=True, blank=True
    )
    
    class Meta:
        db_table = 'teacher_subjects'
        unique_together = ['teacher', 'subject']
        verbose_name = 'Teacher Subject Assignment'
        verbose_name_plural = 'Teacher Subject Assignments'
    
    def __str__(self):
        teacher = self.teacher.full_name if self.teacher else "Unknown"
        subject = self.subject.name if self.subject else "Unknown"
        return f"{teacher} -> {subject}"


class StudentSubject(models.Model):
    """Many-to-Many relationship for Student enrollment in Subjects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, 
        related_name='enrolled_subjects', null=True, blank=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='enrolled_students', null=True, blank=True
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, 
        related_name='student_enrollments', null=True, blank=True
    )
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_subjects'
        unique_together = ['student', 'subject', 'semester']
        verbose_name = 'Student Subject Enrollment'
        verbose_name_plural = 'Student Subject Enrollments'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        subject = self.subject.code if self.subject else "Unknown"
        return f"{student} - {subject}"


# ==================== ACADEMIC MANAGEMENT ====================

class Assignment(models.Model):
    """Assignment model for academic assignments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='assignments', null=True, blank=True
    )
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='created_assignments', null=True, blank=True
    )
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date']
        db_table = 'assignments'
    
    def __str__(self):
        code = self.subject.code if self.subject else "Unknown"
        return f"{code} - {self.title}"


class SubmissionHistory(models.Model):
    """Student submission for assignments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, 
        related_name='submissions', null=True, blank=True
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, 
        related_name='submissions', null=True, blank=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(max_length=500, blank=True)
    file_upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    submission_text = models.TextField(blank=True)
    
    class Meta:
        db_table = 'submission_history'
        unique_together = ['assignment', 'student']
        verbose_name = 'Assignment Submission'
        verbose_name_plural = 'Assignment Submissions'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        assignment = self.assignment.title if self.assignment else "Unknown"
        return f"{student} - {assignment}"


class Grade(models.Model):
    """Grade for a submission"""
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'), ('A', 'A (85-89)'), ('A-', 'A- (80-84)'),
        ('B+', 'B+ (75-79)'), ('B', 'B (70-74)'), ('B-', 'B- (65-69)'),
        ('C+', 'C+ (60-64)'), ('C', 'C (55-59)'), ('C-', 'C- (50-54)'),
        ('D', 'D (40-49)'), ('F', 'F (Below 40)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(
        SubmissionHistory, on_delete=models.CASCADE, 
        related_name='grade', null=True, blank=True
    )
    grade_value = models.CharField(max_length=2, choices=GRADE_CHOICES)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    graded_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='graded_assignments', null=True, blank=True
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
    
    def __str__(self):
        if self.submission and self.submission.student:
            return f"{self.submission.student.enrollment_number} - {self.grade_value}"
        return f"Grade: {self.grade_value}"


class Attendance(models.Model):
    """Attendance record for students"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='attendance_records', null=True, blank=True
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, 
        related_name='attendance_records', null=True, blank=True
    )
    session_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='marked_attendance', null=True, blank=True
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance'
        unique_together = ['subject', 'student', 'session_date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        subject = self.subject.code if self.subject else "Unknown"
        return f"{student} - {subject} - {self.session_date}"


# ==================== ADMINISTRATION ====================

class Event(models.Model):
    """Academic/Administrative events"""
    EVENT_TYPES = [
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('seminar', 'Seminar'),
        ('workshop', 'Workshop'),
        ('holiday', 'Holiday'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    location = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(
        Admin, on_delete=models.CASCADE, 
        related_name='created_events', null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date']
        db_table = 'events'
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"


# ==================== ACADEMIC SCHEDULING ====================

class Holiday(models.Model):
    """Holiday/Break management"""
    HOLIDAY_TYPES = [
        ('public', 'Public Holiday'),
        ('academic', 'Academic Break'),
        ('religious', 'Religious'),
        ('national', 'National'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default='public')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        db_table = 'holidays'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
    
    def __str__(self):
        return f"{self.name} ({self.start_date})"
    
    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1


class Exam(models.Model):
    """Examination scheduling"""
    EXAM_TYPES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('practical', 'Practical'),
        ('viva', 'Viva/Oral'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='exams', null=True, blank=True
    )
    exam_date = models.DateField()
    exam_time = models.TimeField()
    duration_minutes = models.IntegerField(default=120)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='midterm')
    room = models.CharField(max_length=50, blank=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['exam_date', 'exam_time']
        db_table = 'exams'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
    
    def __str__(self):
        subject = self.subject.code if self.subject else "Unknown"
        return f"{subject} - {self.exam_type} ({self.exam_date})"


class Timetable(models.Model):
    """Class schedule/timetable"""
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, 
        related_name='timetable_slots', null=True, blank=True
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='timetable_slots', null=True, blank=True
    )
    day = models.CharField(max_length=15, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day', 'start_time']
        db_table = 'timetables'
        unique_together = ['day', 'start_time', 'room']
        verbose_name = 'Timetable Slot'
        verbose_name_plural = 'Timetable Slots'
    
    def __str__(self):
        subject = self.subject.code if self.subject else "Unknown"
        return f"{self.day} {self.start_time}-{self.end_time}: {subject} in {self.room}"

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
             raise ValidationError("End time must be after start time")

        # Teacher conflict
        if self.teacher:
            conflicts = Timetable.objects.filter(
                day=self.day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                teacher=self.teacher,
                is_active=True
            ).exclude(pk=self.pk)
            
            if conflicts.exists():
                raise ValidationError(f"Teacher {self.teacher.full_name} is already booked at this time.")
            
        # Program/Semester conflict (Class)
        if self.program and self.semester:
            conflicts = Timetable.objects.filter(
                day=self.day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                program=self.program,
                semester=self.semester,
                is_active=True
            ).exclude(pk=self.pk)
            
            if conflicts.exists():
                raise ValidationError(f"Semester {self.semester.number} of {self.program.name} is already booked at this time.")
        
        # Room conflict
        if self.room:
            conflicts = Timetable.objects.filter(
                 day=self.day,
                 start_time__lt=self.end_time,
                 end_time__gt=self.start_time,
                 room=self.room,
                 is_active=True
            ).exclude(pk=self.pk)
            
            if conflicts.exists():
                 raise ValidationError(f"Room {self.room} is occupied at this time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# ==================== MANAGEMENT/FINANCIAL ====================

class Fee(models.Model):
    """Student fee collection"""
    FEE_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partially Paid'),
        ('waived', 'Waived'),
    ]
    
    FEE_TYPES = [
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('exam', 'Exam Fee'),
        ('lab', 'Lab Fee'),
        ('library', 'Library Fee'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, 
        related_name='fees', null=True, blank=True
    )
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES, default='tuition')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FEE_STATUS, default='pending')
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE,
        related_name='fee_records', null=True, blank=True
    )
    receipt_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        db_table = 'fees'
        verbose_name = 'Fee Record'
        verbose_name_plural = 'Fee Records'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        return f"{student} - {self.fee_type} ({self.status})"
    
    @property
    def balance(self):
        return self.amount - self.paid_amount


class Expense(models.Model):
    """Institutional expense tracking"""
    EXPENSE_CATEGORIES = [
        ('salaries', 'Salaries & Wages'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('equipment', 'Equipment'),
        ('events', 'Events'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    vendor = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    approved_by = models.ForeignKey(
        Admin, on_delete=models.SET_NULL, 
        related_name='approved_expenses', null=True, blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        related_name='expenses', null=True, blank=True
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date']
        db_table = 'expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
    
    def __str__(self):
        return f"{self.title} - PKR {self.amount}"





class Account(models.Model):
    """Financial account management"""
    ACCOUNT_TYPES = [
        ('bank', 'Bank Account'),
        ('cash', 'Cash'),
        ('petty_cash', 'Petty Cash'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='bank')
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"{self.name} ({self.account_type})"


class LibraryBook(models.Model):
    """Library book management"""
    BOOK_STATUS = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    location = models.CharField(max_length=50, blank=True)  # Shelf/Row
    status = models.CharField(max_length=20, choices=BOOK_STATUS, default='available')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        db_table = 'library_books'
        verbose_name = 'Library Book'
        verbose_name_plural = 'Library Books'
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class BookBorrowing(models.Model):
    """Book borrowing records"""
    BORROW_STATUS = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        LibraryBook, on_delete=models.CASCADE, 
        related_name='borrowings'
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, 
        related_name='book_borrowings', null=True, blank=True
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='book_borrowings', null=True, blank=True
    )
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BORROW_STATUS, default='borrowed')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-borrowed_date']
        db_table = 'book_borrowings'
        verbose_name = 'Book Borrowing'
        verbose_name_plural = 'Book Borrowings'
    
    def __str__(self):
        borrower = self.student.full_name if self.student else (self.teacher.full_name if self.teacher else "Unknown")
        return f"{self.book.title} - {borrower}"

    def clean(self):
        if not self.student and not self.teacher:
            raise ValidationError("Either a student or a teacher must be the borrower.")
            
        if self.pk is None and self.status == 'borrowed':
             if self.book.copies_available < 1:
                 raise ValidationError(f"Book '{self.book.title}' is not available.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if not is_new:
            try:
                old = BookBorrowing.objects.get(pk=self.pk)
                if old.status == 'borrowed' and self.status == 'returned':
                    self.book.copies_available += 1
                    self.book.save()
            except BookBorrowing.DoesNotExist:
                pass

        self.clean()
        
        if is_new and self.status == 'borrowed':
             self.book.copies_available -= 1
             self.book.save()
             
        super().save(*args, **kwargs)