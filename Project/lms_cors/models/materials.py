from django.db import models
import uuid


class Material(models.Model):
    """Class materials uploaded by teachers"""
    MATERIAL_TYPES = [
        ('lecture_notes', 'Lecture Notes'),
        ('slides', 'Slides'),
        ('assignment', 'Assignment'),
        ('reference', 'Reference'),
        ('video', 'Video'),
        ('outline', 'Course Outline'),
        ('datesheet', 'Date Sheet'),
        ('other', 'Other'),
    ]

    ACCESS_LEVELS = [
        ('public', 'All Students'),
        ('class_only', 'Class Only'),
        ('restricted', 'Restricted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='materials', null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE, 
        related_name='uploaded_materials', null=True, blank=True
    )
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='other')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='class_only')
    file_upload = models.FileField(upload_to='materials/', blank=True, null=True)
    file_url = models.URLField(max_length=500, blank=True)
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
    
    def __str__(self):
        subject = self.subject.code if self.subject else "Unknown"
        return f"{subject} - {self.title}"


class Announcement(models.Model):
    """Class announcements by teachers"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE, 
        related_name='announcements', null=True, blank=True
    )
    created_by = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE, 
        related_name='announcements', null=True, blank=True
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    send_notification = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'announcements'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        subject = self.subject.code if self.subject else "General"
        return f"{subject} - {self.title}"


class ActivityLog(models.Model):
    """Activity logging for admin dashboard"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('upload', 'Upload'),
        ('download', 'Download'),
        ('grade', 'Grade'),
        ('attendance', 'Attendance'),
        ('announcement', 'Announcement'),
    ]
    
    USER_TYPES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, 
        related_name='activity_logs', null=True, blank=True
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    model_name = models.CharField(max_length=50, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        user = self.user.username if self.user else "Unknown"
        return f"{user} - {self.action_type} - {self.description[:50]}"