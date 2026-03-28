from django.db import models
import uuid


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
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='attendance_records', null=True, blank=True
    )
    student = models.ForeignKey(
        'lms_cors.Student', on_delete=models.CASCADE, 
        related_name='attendance_records', null=True, blank=True
    )
    session_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE, 
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
