from django.db import models
import uuid
from .base import BaseProfile
from .academic import generate_sequential_id


class Student(BaseProfile):
    """Student model extending BaseProfile"""
    enrollment_number = models.CharField(max_length=20, unique=True, blank=True)
    program = models.ForeignKey(
        'lms_cors.Program', on_delete=models.CASCADE, 
        related_name='students_legacy', null=True, blank=True
    )
    session = models.ForeignKey(
        'lms_cors.AcademicSession', on_delete=models.CASCADE,
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
        
        if not self.user and not getattr(self, '_skip_auto_user_creation', False):
            self.create_user_account()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.enrollment_number})"


class StudentSemesterHistory(models.Model):
    """Audit trail for semester progression decisions."""

    ACTION_CHOICES = [
        ('promoted', 'Promoted'),
        ('held', 'Held'),
        ('graduated', 'Graduated')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'lms_cors.Student',
        on_delete=models.CASCADE,
        related_name='semester_histories'
    )
    session = models.ForeignKey(
        'lms_cors.AcademicSession',
        on_delete=models.CASCADE,
        related_name='promotion_histories'
    )
    from_semester = models.ForeignKey(
        'lms_cors.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_from_semester'
    )
    to_semester = models.ForeignKey(
        'lms_cors.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_to_semester'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='promoted')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_semester_history'
        ordering = ['-created_at']

    def __str__(self):
        from_number = self.from_semester.number if self.from_semester else 'N/A'
        to_number = self.to_semester.number if self.to_semester else 'N/A'
        return f"{self.student.enrollment_number}: {from_number} -> {to_number} ({self.action})"


class Teacher(BaseProfile):
    """Teacher model extending BaseProfile"""
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(
        'lms_cors.Department', on_delete=models.CASCADE, 
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
        
        if not self.user and not getattr(self, '_skip_auto_user_creation', False):
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
    role = models.CharField(max_length=50)
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
        
        if not self.user and not getattr(self, '_skip_auto_user_creation', False):
            self.create_user_account()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.admin_id})"


class TeacherSubject(models.Model):
    """Many-to-Many relationship between Teacher and Subject"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, 
        related_name='teaching_subjects', null=True, blank=True
    )
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='assigned_teachers', null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    
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
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='enrolled_students', null=True, blank=True
    )
    semester = models.ForeignKey(
        'lms_cors.Semester', on_delete=models.CASCADE, 
        related_name='student_enrollments', null=True, blank=True
    )
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_subjects'
        unique_together = ['student', 'subject', 'semester']
        ordering = ['enrollment_date', 'student', 'subject']
        verbose_name = 'Student Subject Enrollment'
        verbose_name_plural = 'Student Subject Enrollments'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        subject = self.subject.code if self.subject else "Unknown"
        return f"{student} - {subject}"
