from django.db import models
import uuid


class Assignment(models.Model):
    """Assignment model for academic assignments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='assignments', null=True, blank=True
    )
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE, 
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
        'lms_cors.Student', on_delete=models.CASCADE, 
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
        'lms_cors.Teacher', on_delete=models.CASCADE, 
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
