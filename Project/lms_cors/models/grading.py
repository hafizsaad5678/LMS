"""
Professional Grading Management System Models
Supports custom assessment components with full teacher control
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class GradeComponent(models.Model):
    """
    Custom grading components created by teachers
    Examples: Quiz, Assignment, Midterm, Sessional, Attendance, etc.
    """
    COMPONENT_TYPES = [
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('sessional', 'Sessional/Internal'),
        ('attendance', 'Attendance'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('lab', 'Lab Work'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('locked', 'Locked'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE,
        related_name='grade_components'
    )
    created_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE,
        related_name='created_components'
    )
    
    name = models.CharField(max_length=100)  # e.g., "Quiz 1", "Midterm Exam"
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES, default='custom')
    description = models.TextField(blank=True)
    
    max_marks = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    weightage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage weightage in final grade"
    )
    
    # Visibility & Control
    is_visible_to_students = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    date_conducted = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Order for display
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'grade_components'
        ordering = ['display_order', 'created_at']
        verbose_name = 'Grade Component'
        verbose_name_plural = 'Grade Components'
    
    def __str__(self):
        return f"{self.subject.code} - {self.name} ({self.max_marks} marks)"


class StudentMark(models.Model):
    """
    Individual student marks for each grade component
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(
        GradeComponent, on_delete=models.CASCADE,
        related_name='student_marks'
    )
    student = models.ForeignKey(
        'lms_cors.Student', on_delete=models.CASCADE,
        related_name='component_marks'
    )
    
    marks_obtained = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )
    
    remarks = models.TextField(blank=True)
    is_absent = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False, help_text="Lock grade to prevent editing")
    
    # Audit trail
    graded_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.SET_NULL,
        null=True, related_name='graded_marks'
    )
    graded_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_marks'
        unique_together = ['component', 'student']
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'
    
    def __str__(self):
        marks = self.marks_obtained if self.marks_obtained else 'N/A'
        return f"{self.student.enrollment_number} - {self.component.name}: {marks}"
    
    @property
    def percentage(self):
        if self.marks_obtained and self.component.max_marks:
            return round((float(self.marks_obtained) / float(self.component.max_marks)) * 100, 2)
        return 0
    
    @property
    def weighted_marks(self):
        if self.marks_obtained and self.component.max_marks and self.component.weightage:
            return round(
                (float(self.marks_obtained) / float(self.component.max_marks)) * float(self.component.weightage),
                2
            )
        return 0


class MarkEditHistory(models.Model):
    """
    Audit trail for mark changes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_mark = models.ForeignKey(
        StudentMark, on_delete=models.CASCADE,
        related_name='edit_history'
    )
    
    old_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    new_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    old_remarks = models.TextField(blank=True)
    new_remarks = models.TextField(blank=True)
    
    changed_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.SET_NULL,
        null=True, related_name='mark_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'mark_edit_history'
        ordering = ['-changed_at']
        verbose_name = 'Mark Edit History'
        verbose_name_plural = 'Mark Edit Histories'
    
    def __str__(self):
        return f"{self.student_mark} - Changed at {self.changed_at}"


class GradingScheme(models.Model):
    """
    Grading scheme for converting percentages to letter grades
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE,
        related_name='grading_schemes', null=True, blank=True
    )
    
    name = models.CharField(max_length=100, default="Default Grading Scheme")
    is_default = models.BooleanField(default=False)
    
    # Grade boundaries (percentage)
    a_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=90)
    a_min = models.DecimalField(max_digits=5, decimal_places=2, default=85)
    a_minus_min = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    b_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    b_min = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    b_minus_min = models.DecimalField(max_digits=5, decimal_places=2, default=65)
    c_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=60)
    c_min = models.DecimalField(max_digits=5, decimal_places=2, default=55)
    c_minus_min = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    d_min = models.DecimalField(max_digits=5, decimal_places=2, default=40)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=40)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grading_schemes'
        verbose_name = 'Grading Scheme'
        verbose_name_plural = 'Grading Schemes'
    
    def __str__(self):
        return self.name
    
    def get_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= float(self.a_plus_min):
            return 'A+'
        elif percentage >= float(self.a_min):
            return 'A'
        elif percentage >= float(self.a_minus_min):
            return 'A-'
        elif percentage >= float(self.b_plus_min):
            return 'B+'
        elif percentage >= float(self.b_min):
            return 'B'
        elif percentage >= float(self.b_minus_min):
            return 'B-'
        elif percentage >= float(self.c_plus_min):
            return 'C+'
        elif percentage >= float(self.c_min):
            return 'C'
        elif percentage >= float(self.c_minus_min):
            return 'C-'
        elif percentage >= float(self.d_min):
            return 'D'
        return 'F'
    
    def is_passing(self, percentage):
        return percentage >= float(self.passing_marks)


class StudentGradeSummary(models.Model):
    """
    Cached summary of student's overall grade for a subject
    Updated when marks change
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'lms_cors.Student', on_delete=models.CASCADE,
        related_name='grade_summaries'
    )
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE,
        related_name='student_summaries'
    )
    
    total_marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_max_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    weighted_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    letter_grade = models.CharField(max_length=2, default='F')
    is_passing = models.BooleanField(default=False)
    
    # Visibility
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.SET_NULL,
        null=True, related_name='published_summaries'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_grade_summaries'
        unique_together = ['student', 'subject']
        verbose_name = 'Student Grade Summary'
        verbose_name_plural = 'Student Grade Summaries'
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.subject.code}: {self.letter_grade}"

class Quiz(models.Model):
    """
    Electronic quiz model with dynamic questions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE,
        related_name='quizzes'
    )
    created_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE,
        related_name='created_quizzes'
    )
    time_limit_minutes = models.IntegerField(default=30)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Integration with GradeComponent
    grade_component = models.OneToOneField(
        GradeComponent, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='linked_quiz'
    )
    
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    """
    Question for a quiz
    """
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    correct_answer_text = models.TextField(blank=True, help_text="Correct answer for short answer questions")
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order']

class QuizOption(models.Model):
    """
    MCQ Option for a question
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_options'

class QuizAttempt(models.Model):
    """
    Student attempt at a quiz
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('auto_submitted', 'Auto Submitted'),
        ('force_ended', 'Force Ended'),
        ('evaluated', 'Evaluated')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('lms_cors.Student', on_delete=models.CASCADE, related_name='quiz_attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_attempts')
    answers = models.JSONField(default=dict, blank=True)
    flagged_questions = models.JSONField(default=list, blank=True)
    start_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    is_submitted = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quiz_attempts'
        unique_together = ['quiz', 'student']

    def save(self, *args, **kwargs):
        if not self.user_id and self.student_id and getattr(self.student, 'user_id', None):
            self.user_id = self.student.user_id

        if not self.end_time:
            limit_minutes = self.quiz.time_limit_minutes if self.quiz and self.quiz.time_limit_minutes else 30
            self.end_time = timezone.now() + timedelta(minutes=limit_minutes)

        super().save(*args, **kwargs)

    @property
    def is_locked(self):
        return self.status in {'submitted', 'auto_submitted', 'force_ended', 'evaluated'} or self.is_completed

    @property
    def is_expired(self):
        return bool(self.end_time and timezone.now() >= self.end_time)

class QuizAnswer(models.Model):
    """
    Student's specific answer to a question in an attempt
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answer_entries')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuizOption, on_delete=models.SET_NULL, null=True, blank=True)
    answer_text = models.TextField(blank=True) # For non-MCQ
    marks_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='not_visited')
    is_flagged = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quiz_answers'

