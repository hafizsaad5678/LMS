from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Avg
from ..models.people import Student, Teacher, TeacherSubject, StudentSubject
from ..models.academic import Department, Program, AcademicSession, Subject
from ..models.management import Fee, Expense, Account
from ..models.assignments import Assignment, SubmissionHistory, Grade
from ..models.grading import StudentMark, StudentGradeSummary, QuizAttempt
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

    fees = Fee.objects.filter(status='paid').order_by('-updated_at')[:recent_limit]
    for f in fees:
        name = f.student.full_name if f.student else f.remarks or f.receipt_number or "General Revenue"
        activities.append({
            'id': f"fee-{f.id}-paid",
            'message': f"Revenue received: {name} (PKR {f.amount})",
            'timestamp': f.updated_at or f.created_at,
            'type': 'finance',
            'icon': 'bi bi-cash-coin',
            'color': 'text-success'
        })

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
    classes = TeacherSubject.objects.filter(
        teacher=teacher,
        subject__isnull=False,
        subject__semester__status='active'
    )
    classes_count = classes.count()
    
    # Students count (distinct students across all assigned subjects)
    subject_ids = classes.values_list('subject_id', flat=True)
    students_count = StudentSubject.objects.filter(subject_id__in=subject_ids).values('student_id').distinct().count()
    
    # Assignments count
    assignments = Assignment.objects.filter(
        created_by=teacher,
        subject__semester__status='active'
    ).annotate(
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
    enrolled_subjects = student.enrolled_subjects.filter(
        subject__semester__number=student.current_semester
    ).annotate(
        total_components=Count('subject__grade_components', distinct=True),
        total_assignments=Count('subject__assignments', distinct=True)
    )
    enrolled_count = enrolled_subjects.count()
    
    # Grading Progress (graded subjects / active subjects)
    # This is a bit complex, we'll use a simplified version of the logic in grade_report
    assignment_grades = Grade.objects.filter(
        submission__student=student,
        submission__assignment__subject__semester__number=student.current_semester
    )
    component_marks = StudentMark.objects.filter(
        student=student,
        component__is_visible_to_students=True,
        component__subject__semester__number=student.current_semester
    )
    
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
    attendance_records = student.attendance_records.filter(
        subject__semester__number=student.current_semester
    )
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_charts(request):
    """
    Endpoint for Admin Dashboard charts:
    - User growth (students and teachers registered over the last 6 months)
    - Course enrollment stats (students per program)
    """
    import datetime
    now = timezone.now()
    months = []
    labels = []
    student_counts = []
    teacher_counts = []
    
    # Generate last 6 months list (chronological order)
    for i in range(5, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        month_date = datetime.date(y, m, 1)
        months.append((y, m))
        labels.append(month_date.strftime('%b %Y'))
        student_counts.append(0)
        teacher_counts.append(0)

    # Fetch created_at timestamps for last 180 days
    start_date = now - timedelta(days=180)
    student_dates = Student.objects.filter(created_at__gte=start_date).values_list('created_at', flat=True)
    teacher_dates = Teacher.objects.filter(created_at__gte=start_date).values_list('created_at', flat=True)

    for dt in student_dates:
        if dt:
            for idx, (y, m) in enumerate(months):
                if dt.year == y and dt.month == m:
                    student_counts[idx] += 1
                    break

    for dt in teacher_dates:
        if dt:
            for idx, (y, m) in enumerate(months):
                if dt.year == y and dt.month == m:
                    teacher_counts[idx] += 1
                    break

    # Program Enrollments
    programs = Program.objects.annotate(
        student_count=Count('students_legacy')
    ).values('name', 'student_count')
    
    enrollment_labels = [p['name'] for p in programs]
    enrollment_values = [p['student_count'] for p in programs]

    # Clean up empty or cut-off labels to make them look beautiful
    cleaned_labels = []
    for lbl in enrollment_labels:
        if not lbl:
            cleaned_labels.append("General Program")
        elif lbl.lower() == 'pp':
            cleaned_labels.append("Pre-Professional")
        elif lbl.lower() == 'se':
            cleaned_labels.append("Software Engineering")
        elif lbl.lower() == 'pak':
            cleaned_labels.append("Pakistan Studies")
        elif lbl.startswith('mputer'):
            cleaned_labels.append("Computer Science (BSCS)")
        else:
            # Capitalize each word nicely
            cleaned_labels.append(lbl.title())
    enrollment_labels = cleaned_labels

    return Response({
        'user_growth': {
            'labels': labels,
            'students': student_counts,
            'teachers': teacher_counts
        },
        'course_enrollment': {
            'labels': enrollment_labels,
            'values': enrollment_values
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_charts(request):
    """
    Endpoint for Teacher Dashboard charts:
    - Student performance (avg score per subject)
    - Assignment completion (submitted vs pending for last 5 assignments)
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=404)

    # Active classes/subjects taught by this teacher
    classes = TeacherSubject.objects.filter(
        teacher=teacher,
        subject__isnull=False,
        subject__semester__status='active'
    )

    performance_labels = []
    performance_values = []
    
    for ts in classes:
        subj = ts.subject
        if not subj:
            continue
        
        # 1. Try StudentGradeSummary
        avg_score = StudentGradeSummary.objects.filter(subject=subj).aggregate(Avg('weighted_percentage'))['weighted_percentage__avg']
        
        # 2. Try StudentMark fallback
        if avg_score is None:
            marks = StudentMark.objects.filter(component__subject=subj, marks_obtained__isnull=False)
            pct_list = []
            if marks.exists():
                for m in marks:
                    max_marks = float(m.component.max_marks or 0)
                    if max_marks > 0:
                        pct_list.append((float(m.marks_obtained) / max_marks) * 100)
            
            # 3. Add Assignment Grades
            grades = Grade.objects.filter(submission__assignment__subject=subj, marks_obtained__isnull=False)
            for g in grades:
                total = float(g.submission.assignment.total_marks or 0)
                if total > 0:
                    pct_list.append((float(g.marks_obtained) / total) * 100)
            
            # 4. Add Quiz Attempts
            attempts = QuizAttempt.objects.filter(quiz__subject=subj, score__isnull=False)
            for qa in attempts:
                total = float(qa.quiz.total_marks or 0)
                if total > 0:
                    pct_list.append((float(qa.score) / total) * 100)
            
            avg_score = sum(pct_list) / len(pct_list) if pct_list else None
                
        if avg_score is None:
            avg_score = 0.0

        performance_labels.append(f"{subj.name} ({subj.code})")
        performance_values.append(round(float(avg_score), 2))

    # Assignments created by this teacher in active semesters
    latest_assignments = Assignment.objects.filter(
        created_by=teacher,
        subject__semester__status='active'
    ).order_by('-created_at')[:5]

    assignment_labels = []
    submitted_counts = []
    pending_counts = []

    for a in latest_assignments:
        sub_count = a.submissions.count()
        total_students = StudentSubject.objects.filter(
            subject=a.subject,
            semester=a.subject.semester
        ).count()
        pending = max(0, total_students - sub_count)
        
        # Clean title misspelling
        title = a.title
        title = title.replace(',,', ', ')
        title = title.replace('asignment', 'Assignment')
        title = title.title()
        
        assignment_labels.append(title)
        submitted_counts.append(sub_count)
        pending_counts.append(pending)

    return Response({
        'student_performance': {
            'labels': performance_labels,
            'values': performance_values
        },
        'assignment_completion': {
            'labels': assignment_labels,
            'submitted': submitted_counts,
            'pending': pending_counts
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def student_charts(request):
    """
    Endpoint for Student Dashboard charts:
    - Course progress (% marks per subject)
    - Quiz trend (score percentage per quiz attempt for the last 5 attempts)
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'detail': 'Student profile not found.'}, status=404)

    enrolled_subjects = student.enrolled_subjects.filter(
        subject__semester__number=student.current_semester
    )

    progress_labels = []
    progress_values = []

    for es in enrolled_subjects:
        subj = es.subject
        if not subj:
            continue
        
        # 1. Try StudentGradeSummary
        summary = StudentGradeSummary.objects.filter(student=student, subject=subj).first()
        pct = float(summary.weighted_percentage) if summary else 0.0
        
        # 2. Try StudentMark fallback
        if not pct:
            pct_list = []
            marks = StudentMark.objects.filter(student=student, component__subject=subj, marks_obtained__isnull=False)
            if marks.exists():
                for m in marks:
                    max_marks = float(m.component.max_marks or 0)
                    if max_marks > 0:
                        pct_list.append((float(m.marks_obtained) / max_marks) * 100)
            
            # 3. Add Assignment Grades fallback
            grades = Grade.objects.filter(submission__student=student, submission__assignment__subject=subj, marks_obtained__isnull=False)
            for g in grades:
                total = float(g.submission.assignment.total_marks or 0)
                if total > 0:
                    pct_list.append((float(g.marks_obtained) / total) * 100)
            
            # 4. Add Quiz Attempts fallback
            attempts = QuizAttempt.objects.filter(student=student, quiz__subject=subj, score__isnull=False)
            for qa in attempts:
                total = float(qa.quiz.total_marks or 0)
                if total > 0:
                    pct_list.append((float(qa.score) / total) * 100)
                    
            pct = sum(pct_list) / len(pct_list) if pct_list else 0.0
            
        if not pct:
            pct = 0.0

        progress_labels.append(f"{subj.name} ({subj.code})")
        progress_values.append(round(pct, 2))

    # Quiz Attempts
    quiz_attempts = QuizAttempt.objects.filter(
        student=student
    ).order_by('-started_at')[:5]

    quiz_labels = []
    quiz_values = []

    # Reverse to show chronological order
    for qa in reversed(quiz_attempts):
        total = float(qa.quiz.total_marks) if qa.quiz and qa.quiz.total_marks else 100.0
        score_pct = (float(qa.score) / total) * 100 if total > 0 else 0.0
        
        quiz_title = qa.quiz.title if qa.quiz else "Quiz"
        subj_name = ""
        if qa.quiz and qa.quiz.subject:
            subj_name = f" ({qa.quiz.subject.code})"
        quiz_labels.append(f"{quiz_title}{subj_name}")
        quiz_values.append(round(score_pct, 2))

    return Response({
        'course_progress': {
            'labels': progress_labels,
            'values': progress_values
        },
        'quiz_trend': {
            'labels': quiz_labels,
            'values': quiz_values
        }
    })

