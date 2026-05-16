from django.db import models
from django.core.exceptions import ValidationError
import uuid


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
        'lms_cors.Admin', on_delete=models.CASCADE, 
        related_name='created_events', null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date']
        db_table = 'events'
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"


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
        'lms_cors.Subject', on_delete=models.CASCADE, 
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
    phase = models.CharField(max_length=50, blank=True, null=True, help_text="Academic phase (e.g., Spring 2024, Fall 2023)")
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
    """
    Class schedule / timetable slot.

    Semester locking rule:
      - When a semester ends, set semester.is_active = False (do NOT delete slots).
      - The ViewSet filters by semester__status='active' so old slots are hidden
        from the live timetable but remain in the database for historical records.

    Schedule types:
      - permanent  → repeats every week for the semester duration
      - temporary  → applies to one specific date only (specific_date is required)

    Future upgrade path (not implemented yet):
      You can later add `effective_start_date` and `effective_end_date` DateFields
      to handle overlapping semesters, exam-period extensions, or academic holidays
      without changing the core filtering logic.
    """

    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    SCHEDULE_TYPE_CHOICES = [
        ('permanent', 'Permanent (every week)'),
        ('temporary', 'Temporary (specific date only)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        'lms_cors.Subject', on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    teacher = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    day = models.CharField(max_length=15, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    program = models.ForeignKey(
        'lms_cors.Program', on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    semester = models.ForeignKey(
        'lms_cors.Semester', on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True
    )
    academic_session = models.ForeignKey(
        'lms_cors.AcademicSession', on_delete=models.CASCADE,
        related_name='timetable_slots', null=True, blank=True,
        help_text="Explicitly binds timetable to a specific year/session to separate old records"
    )

    # --- Schedule type (permanent vs temporary) ---
    schedule_type = models.CharField(
        max_length=15,
        choices=SCHEDULE_TYPE_CHOICES,
        default='permanent',
        help_text="Permanent = repeats every week. Temporary = one specific date only."
    )
    specific_date = models.DateField(
        null=True, blank=True,
        help_text="Only required when schedule_type is 'temporary'."
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
        type_label = f" [{self.schedule_type}]" if self.schedule_type == 'temporary' else ""
        return f"{self.day} {self.start_time}-{self.end_time}: {subject} in {self.room}{type_label}"

    def clean(self):
        # ── Basic time validation ──────────────────────────────────────
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        # ── Schedule type validation ───────────────────────────────────
        if self.schedule_type == 'temporary' and not self.specific_date:
            raise ValidationError(
                {"specific_date": "A specific date is required for temporary schedules."}
            )
        if self.schedule_type == 'permanent':
            # Prevent accidental date being stored on a permanent slot
            self.specific_date = None

        # ── Teacher conflict ───────────────────────────────────────────
        if self.teacher:
            conflicts = Timetable.objects.filter(
                day=self.day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                teacher=self.teacher,
                is_active=True,
            ).exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError(
                    f"Teacher {self.teacher.full_name} is already booked at this time."
                )

        # ── Program / Semester (class group) conflict ──────────────────
        if self.program and self.semester:
            conflicts = Timetable.objects.filter(
                day=self.day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                program=self.program,
                semester=self.semester,
                is_active=True,
            ).exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError(
                    f"Semester {self.semester.number} of {self.program.name} "
                    f"is already booked at this time."
                )

        # ── Room conflict ──────────────────────────────────────────────
        if self.room:
            conflicts = Timetable.objects.filter(
                day=self.day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                room=self.room,
                is_active=True,
            ).exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError(f"Room {self.room} is occupied at this time.")

    def save(self, *args, **kwargs):
        if self.semester and hasattr(self.semester, 'session'):
            self.academic_session = self.semester.session
        self.clean()
        super().save(*args, **kwargs)
