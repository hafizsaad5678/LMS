from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from ..models.people import Student, Teacher, TeacherSubject, StudentSubject
from ..models.academic import Department, Program, AcademicSession, Subject
from ..models.management import Fee, Expense, Account
from ..models.assignments import Assignment, SubmissionHistory, Grade
from ..models.grading import StudentMark
from ..models.materials import Announcement
from ..models.scheduling import Holiday, Exam, Event, Timetable
from ..models.library import LibraryBook, BookBorrowing
from ..permissions import IsAdminUser, IsTeacherUser, IsStudentUser
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard_stats(request):
    """
    Unified endpoint for Admin Dashboard statistics and recent activities.
    Reduces multiple API calls from the frontend and avoids N+1 issues.
    """
    # 1. Entity Counts
    counts = {
        'students': Student.objects.count(),
        'teachers': Teacher.objects.count(),
        'departments': Department.objects.count(),
        'programs': Program.objects.count(),
        'sessions': AcademicSession.objects.count(),
        'subjects': Subject.objects.count(),
        'holidays': Holiday.objects.count(),
        'exams': Exam.objects.count(),
        'events': Event.objects.count(),
        'timetables': Timetable.objects.count(),
        'expenses': Expense.objects.count(),
        'accounts': Account.objects.count(),
        'library_books': LibraryBook.objects.count(),
        'borrowings': BookBorrowing.objects.count(),
    }

    # 2. Revenue Statistics
    total_revenue = Fee.objects.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    
    # 3. Recent Activities (Consolidated)
    # We take the most recently updated items from each main entity
    recent_limit = 5
    
    # Helper to format activity
    def format_activity(item, type_label, type_slug, icon, color, name_field='full_name'):
        # Heuristic to determine if created or updated
        action = 'created'
        try:
            if item.updated_at and item.created_at:
                if (item.updated_at - item.created_at).total_seconds() > 5:
                    action = 'updated'
        except Exception:
            pass
        
        name = getattr(item, name_field, 'N/A')
        if not name or name == 'N/A':
            name = getattr(item, 'name', 'N/A')
        if not name or name == 'N/A':
             name = getattr(item, 'title', 'N/A')

        timestamp = getattr(item, 'updated_at', None) or getattr(item, 'created_at', None)

        return {
            'id': f"{type_slug}-{item.id}-{action}",
            'message': f"{type_label} {action}: {name}",
            'timestamp': timestamp,
            'type': type_slug,
            'icon': icon,
            'color': color
        }

    activities = []
    
    # Fetch from entities that have audit fields
    # We use prefetch_related where applicable if we were fetching deeper data, 
    # but here we just need basic fields.
    
    students = Student.objects.all().order_by('-updated_at')[:recent_limit]
    for s in students:
        activities.append(format_activity(s, 'Student', 'student', 'bi bi-person-plus', 'text-success'))

    teachers = Teacher.objects.all().order_by('-updated_at')[:recent_limit]
    for t in teachers:
        activities.append(format_activity(t, 'Teacher', 'teacher', 'bi bi-person-badge', 'text-primary'))

    departments = Department.objects.all().order_by('-updated_at')[:recent_limit]
    for d in departments:
        activities.append(format_activity(d, 'Department', 'department', 'bi bi-building', 'text-info', 'name'))

    programs = Program.objects.all().order_by('-updated_at')[:recent_limit]
    for p in programs:
        activities.append(format_activity(p, 'Program', 'program', 'bi bi-mortarboard', 'text-secondary', 'name'))

    # Sort all by timestamp and take top 10
    activities = [a for a in activities if a['timestamp']]
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Convert timestamps to string for JSON serialization
    final_activities = []
    for a in activities[:10]:
        a['time_iso'] = a['timestamp'].isoformat()
        # Remove the datetime object before returning
        item_copy = {k: v for k, v in a.items() if k != 'timestamp'}
        final_activities.append(item_copy)

    return Response({
        'counts': counts,
        'revenue': total_revenue,
        'recent_activities': final_activities
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_dashboard_stats(request):
    """
    Unified endpoint for Teacher Dashboard statistics and activities.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=404)

    # 1. Stats logic (efficient aggregation)
    # Classes count
    classes = TeacherSubject.objects.filter(teacher=teacher, subject__isnull=False)
    classes_count = classes.count()
    
    # Students count (distinct students across all assigned subjects)
    subject_ids = classes.values_list('subject_id', flat=True)
    students_count = StudentSubject.objects.filter(subject_id__in=subject_ids).values('student_id').distinct().count()
    
    # Assignments count
    assignments = Assignment.objects.filter(created_by=teacher).annotate(
        submission_count=Count('submissions', distinct=True),
        graded_count=Count('submissions__grade', distinct=True)
    )
    assignments_count = assignments.count()
    
    # Pending reviews (submissions - graded)
    pending_reviews = 0
    for a in assignments:
        pending_reviews += max(0, a.submission_count - a.graded_count)
        
    # Upcoming deadlines (next 7 days)
    now = timezone.now()
    next_week = now + timedelta(days=7)
    upcoming_deadlines = assignments.filter(due_date__range=(now, next_week)).count()
    
    # 2. Recent Activities
    activities = []
    # Recent assignments created
    recent_assignments = assignments.order_by('-created_at')[:5]
    for a in recent_assignments:
        activities.append({
            'id': f"assign-{a.id}",
            'message': f"Assignment \"{a.title}\" - {a.submission_count} submissions",
            'time_iso': a.created_at.isoformat(),
            'type': 'assignment',
            'icon': 'bi bi-clipboard-check',
            'color': 'text-primary'
        })
        
    # Recent classes (subjects)
    recent_classes = classes.select_related('subject').order_by('-id')[:5]
    for c in recent_classes:
        subject_name = c.subject.name if c.subject else "Unknown Subject"
        subject_code = c.subject.code if c.subject else "???"
        activities.append({
            'id': f"class-{c.id}",
            'message': f"Class: {subject_name} ({subject_code})",
            'time_iso': now.isoformat(),
            'type': 'class',
            'icon': 'bi bi-book',
            'color': 'text-success'
        })

    return Response({
        'counts': {
            'classes': classes_count,
            'students': students_count,
            'assignments': assignments_count,
            'pending_reviews': pending_reviews,
            'upcoming_deadlines': upcoming_deadlines
        },
        'recent_activities': activities[:8]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def student_dashboard_stats(request):
    """
    Unified endpoint for Student Dashboard statistics and activities.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'detail': 'Student profile not found.'}, status=404)

    # 1. Subjects & GPA
    enrolled_subjects = student.enrolled_subjects.all().annotate(
        total_components=Count('subject__grade_components', distinct=True),
        total_assignments=Count('subject__assignments', distinct=True)
    )
    enrolled_count = enrolled_subjects.count()
    
    # Grading Progress (graded subjects / active subjects)
    # This is a bit complex, we'll use a simplified version of the logic in grade_report
    assignment_grades = Grade.objects.filter(submission__student=student)
    component_marks = StudentMark.objects.filter(student=student, component__is_visible_to_students=True)
    
    graded_subjects_ids = set(assignment_grades.values_list('submission__assignment__subject_id', flat=True))
    graded_subjects_ids.update(component_marks.values_list('component__subject_id', flat=True))
    
    active_subjects_count = enrolled_subjects.filter(
        Q(total_components__gt=0) | Q(total_assignments__gt=0)
    ).count()
    
    grading_progress = f"{len(graded_subjects_ids)}/{active_subjects_count}"
    
    # GPA Calculation (Simplified)
    records = []
    for grade in assignment_grades.select_related('submission__assignment'):
        total = float(grade.submission.assignment.total_marks or 0)
        obtained = float(grade.marks_obtained or 0)
        if total > 0:
            records.append((obtained / total) * 100)
            
    for mark in component_marks:
        records.append(float(mark.percentage or 0))
        
    def get_gp(p):
        if p >= 85: return 4.0
        if p >= 80: return 3.7
        if p >= 75: return 3.3
        if p >= 70: return 3.0
        if p >= 65: return 2.7
        if p >= 61: return 2.3
        if p >= 50: return 2.0
        return 0.0
        
    gpa = 0.0
    if records:
        gpa = sum(get_gp(p) for p in records) / len(records)
    
    # Attendance
    attendance_records = student.attendance_records.all()
    attendance_pct = 0
    if attendance_records.exists():
        present = attendance_records.filter(status='present').count()
        attendance_pct = int((present / attendance_records.count()) * 100)
        
    # Pending Assignments
    now = timezone.now()
    enrolled_subject_ids = enrolled_subjects.values_list('subject_id', flat=True)
    pending_assignments_count = Assignment.objects.filter(
        subject_id__in=enrolled_subject_ids,
        due_date__gt=now
    ).exclude(
        submissions__student=student
    ).count()
    
    # Unread Announcements
    announcements_count = Announcement.objects.filter(
        Q(subject_id__in=enrolled_subject_ids) | Q(subject__isnull=True)
    ).count() # Simplified: counting all relevant ones as "unread"
    
    # 2. Activities
    activities = []
    # Upcoming assignments
    upcoming = Assignment.objects.filter(
        subject_id__in=enrolled_subject_ids,
        due_date__gt=now
    ).exclude(
        submissions__student=student
    ).order_by('due_date')[:3]
    
    for u in upcoming:
        days = (u.due_date - now).days
        time_text = f"Due in {days} days" if days > 1 else "Due soon"
        subj_name = u.subject.name if u.subject else "General"
        activities.append({
            'title': f"Assignment: {u.title}",
            'description': f"{subj_name} • {time_text}",
            'time': time_text,
            'icon': 'bi bi-clipboard-check',
            'color': 'text-warning' if days > 1 else 'text-danger'
        })
        
    # Recent grades
    recent_grades = assignment_grades.select_related('submission__assignment__subject').order_by('-graded_at')[:2]
    for rg in recent_grades:
        subj_name = "Subject"
        if rg.submission and rg.submission.assignment and rg.submission.assignment.subject:
            subj_name = rg.submission.assignment.subject.name

        activities.append({
            'title': f"Grade posted: {subj_name}",
            'description': f"Score: {rg.marks_obtained}/{rg.submission.assignment.total_marks if rg.submission and rg.submission.assignment else '?'}",
            'time': "Recent",
            'icon': 'bi bi-star-fill',
            'color': 'text-success'
        })

    return Response({
        'stats': {
            'enrolledCourses': enrolled_count,
            'gpa': f"{gpa:.2f}",
            'gradingProgress': grading_progress,
            'attendance': f"{attendance_pct}%",
            'pendingAssignments': pending_assignments_count,
            'unreadAnnouncements': announcements_count
        },
        'activities': activities[:5]
    })
