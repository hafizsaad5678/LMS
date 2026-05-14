from collections import defaultdict
from django.db.models import Q, Count, Exists, OuterRef, Sum
from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .base import BaseProfileViewSet, BaseViewSet
from ..models import (
    Student, Teacher, Admin, TeacherSubject, StudentSubject, 
    Grade, StudentMark, Assignment, SubmissionHistory, Subject, Timetable,
    Quiz, QuizAttempt, GradeComponent, Announcement, Exam
)
from ..serializers import (
    StudentSerializer, StudentDetailSerializer,
    TeacherSerializer, TeacherDetailSerializer,
    AdminSerializer,
    TeacherSubjectSerializer, StudentSubjectSerializer,
    SubmissionHistorySerializer, GradeSerializer, AttendanceSerializer,
    AssignmentSerializer, EventSerializer, FeeSerializer, StudentMarkSerializer,
    StudentAssignmentSerializer, AnnouncementSerializer, TimetableSerializer, ExamSerializer
)
from ..permissions import CanManageStudents, IsAdminUser, IsAdminOrTeacher, IsTeacherUser


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_my_classes(request):
    """
    Returns the logged-in teacher's assigned subjects/classes with full academic hierarchy.
    Only accessible by authenticated teachers.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Optional filters
    session_id = request.query_params.get('session')
    subject_id = request.query_params.get('subject')

    # Primary source: direct teacher-subject assignments
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher,
        subject__isnull=False,
        subject__semester__status='active'
    ).select_related(
        'subject',
        'subject__semester',
        'subject__semester__session',
        'subject__semester__program',
        'subject__semester__program__department'
    )

    # Secondary source: subjects appearing in teacher timetable
    timetable_subject_ids = Timetable.objects.filter(
        teacher=teacher,
        subject__isnull=False,
        is_active=True,
        subject__semester__status='active'
    ).values_list('subject_id', flat=True).distinct()

    # Map subject_id -> assignment row (when available)
    teacher_subject_map = {
        str(ts.subject_id): ts
        for ts in teacher_subjects
        if ts.subject_id
    }

    # Consolidate unique subjects from both sources
    subject_map = {
        str(ts.subject.id): ts.subject
        for ts in teacher_subjects
        if ts.subject
    }

    missing_subject_ids = [
        sid for sid in timetable_subject_ids
        if str(sid) not in subject_map
    ]

    if missing_subject_ids:
        fallback_subjects = Subject.objects.filter(id__in=missing_subject_ids).select_related(
            'semester',
            'semester__session',
            'semester__program',
            'semester__program__department'
        )
        for subject in fallback_subjects:
            subject_map[str(subject.id)] = subject

    # Apply optional filters after merge
    if subject_id:
        subject_map = {
            sid: subject
            for sid, subject in subject_map.items()
            if sid == str(subject_id)
        }

    if session_id:
        subject_map = {
            sid: subject
            for sid, subject in subject_map.items()
            if getattr(getattr(subject, 'semester', None), 'session_id', None) and str(subject.semester.session_id) == str(session_id)
        }

    # Build response data with full academic hierarchy
    classes = []
    for sid, subject in subject_map.items():
        semester = subject.semester
        session = semester.session if semester else None
        program = semester.program if semester else None
        department = program.department if program else None

        # Count enrolled students for this subject
        student_count = StudentSubject.objects.filter(subject=subject).count()

        # Keep existing id semantics (TeacherSubject id when present) for compatibility
        ts = teacher_subject_map.get(sid)
        class_row_id = str(ts.id) if ts else str(subject.id)

        classes.append({
            'id': class_row_id,
            'subject_id': str(subject.id),
            'subject_name': subject.name,
            'subject_code': subject.code,
            'credit_hours': subject.credit_hours,
            'description': subject.description or '',
            'student_count': student_count,

            # Semester Information
            'semester': f"Semester {semester.number}" if semester else "N/A",
            'semester_id': str(semester.id) if semester else None,
            'semester_number': semester.number if semester else None,

            # Session Information
            'session_id': str(session.id) if session else None,
            'session_name': session.session_name if session else "N/A",
            'session_code': session.session_code if session else "N/A",

            # Program Information
            'program_name': program.name if program else "N/A",
            'program_code': program.code if program else "N/A",
            'program_id': str(program.id) if program else None,
            'program_level': program.program_level if program else "N/A",

            # Department Information
            'department_name': department.name if department else "N/A",
            'department_code': department.code if department else "N/A",
            'department_id': str(department.id) if department else None,
        })
    
    return Response({'results': classes, 'count': len(classes)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_my_assignments(request):
    """
    Returns assignments created by the logged-in teacher.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    # Get assignments with submission counts using annotation (avoids N+1 queries)
    # Filter out assignments that are already linked to a GradeComponent
    assignments = Assignment.objects.filter(
        created_by=teacher,
        subject__semester__status='active'
    ).exclude(
        Exists(GradeComponent.objects.filter(name=OuterRef('title'), subject=OuterRef('subject')))
    ).select_related(
        'subject', 'subject__semester'
    ).annotate(
        submission_count=Count('submissions', distinct=True),
        graded_count=Count('submissions__grade', distinct=True),
        total_students=Count('subject__enrolled_students', distinct=True)
    ).order_by('-created_at')
    
    assignment_data = []
    for assignment in assignments:
        pending_review_count = max(0, int(assignment.submission_count or 0) - int(assignment.graded_count or 0))
        assignment_data.append({
            'id': str(assignment.id),
            'title': assignment.title,
            'description': assignment.description,
            'subject': str(assignment.subject.id) if assignment.subject else None,
            'subject_name': assignment.subject.name if assignment.subject else 'N/A',
            'subject_code': assignment.subject.code if assignment.subject else 'N/A',
            'class_name': f"{assignment.subject.name} - {assignment.subject.code}" if assignment.subject else 'N/A',
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'total_marks': float(assignment.total_marks),
            'submission_count': assignment.submission_count,
            'submitted': assignment.submission_count,  # Keep for backward compatibility
            'graded_count': assignment.graded_count,
            'pending_review_count': pending_review_count,
            'total_students': assignment.total_students,
            'status': 'active' if assignment.due_date and assignment.due_date > timezone.now() else 'closed',
            'created_at': assignment.created_at.isoformat(),
        })
    
    return Response({'results': assignment_data, 'count': len(assignment_data)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_class_students(request, class_id):
    """
    Returns students enrolled in a specific class/subject taught by the teacher.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Resolve class identifier from multiple sources for compatibility:
    # 1) TeacherSubject.id (legacy/current)
    # 2) Subject.id (class cards merged from timetable)
    # 3) Timetable.id (when provided from schedule contexts)
    teacher_subject = TeacherSubject.objects.filter(
        id=class_id,
        teacher=teacher,
        subject__isnull=False
    ).select_related('subject', 'subject__semester').first()

    subject = teacher_subject.subject if teacher_subject else None

    if not subject:
        subject = Subject.objects.filter(id=class_id).select_related('semester').first()

    if not subject:
        timetable_row = Timetable.objects.filter(
            id=class_id,
            teacher=teacher,
            subject__isnull=False
        ).select_related('subject', 'subject__semester').first()
        subject = timetable_row.subject if timetable_row else None

    if not subject:
        return Response({'detail': 'Class not found or not assigned to you.'}, status=status.HTTP_404_NOT_FOUND)

    has_access = (
        TeacherSubject.objects.filter(teacher=teacher, subject=subject).exists()
        or Timetable.objects.filter(teacher=teacher, subject=subject, is_active=True).exists()
    )

    if not has_access:
        return Response({'detail': 'Class not found or not assigned to you.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Optional filters
    session_id = request.query_params.get('session')

    # Get students enrolled in this subject
    student_subjects = StudentSubject.objects.filter(
        subject=subject
    ).select_related('student', 'student__session')

    if session_id:
        student_subjects = student_subjects.filter(student__session_id=session_id)
    
    students_data = []
    seen_student_ids = set()
    for ss in student_subjects:
        student = ss.student
        if not student or student.id in seen_student_ids:
            continue

        seen_student_ids.add(student.id)
        students_data.append({
            'id': str(student.id),
            'name': student.full_name,
            'roll_no': student.enrollment_number,
            'email': student.email,
            'phone': student.phone,
            'enrollment_date': ss.enrollment_date.isoformat() if ss.enrollment_date else None,
            'session_id': str(student.session.id) if getattr(student, 'session', None) else None,
            'session_name': student.session.session_name if getattr(student, 'session', None) else None,
        })
    
    return Response({
        'results': students_data, 
        'count': len(students_data),
        'class_info': {
            'subject_name': subject.name,
            'subject_code': subject.code,
            'semester': f"Semester {subject.semester.number}" if subject.semester else "N/A"
        }
    })


class StudentViewSet(BaseProfileViewSet):
    queryset = Student.objects.select_related('program', 'program__department', 'program__department__institution', 'session').filter(
        program__isnull=False,
        program__department__is_active=True,
        program__department__institution__is_active=True
    ).filter(Q(session__isnull=True) | Q(session__is_active=True))
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, CanManageStudents]
    search_fields = ['full_name', 'email', 'enrollment_number', 'phone', 'cnic']
    filterset_fields = ['program', 'is_active', 'is_verified', 'is_suspended', 
                       'gender', 'enrollment_year', 'current_semester']
    ordering_fields = ['full_name', 'created_at', 'enrollment_number', 'enrollment_year']
    
    def get_serializer_class(self):
        return StudentDetailSerializer if self.action == 'retrieve' else StudentSerializer

    def _current_enrollments(self, student):
        queryset = student.enrolled_subjects.all()

        if getattr(student, 'session_id', None):
            queryset = queryset.filter(semester__session_id=student.session_id)

        if getattr(student, 'current_semester', None):
            queryset = queryset.filter(semester__number=student.current_semester)

        return queryset

    @staticmethod
    def _grade_point_from_percentage(percentage):
        if percentage >= 85:
            return 4.00
        if percentage >= 80:
            return 3.70
        if percentage >= 75:
            return 3.30
        if percentage >= 70:
            return 3.00
        if percentage >= 65:
            return 2.70
        if percentage >= 61:
            return 2.30
        if percentage >= 50:
            return 2.00
        return 0.00

    @staticmethod
    def _grade_value_from_percentage(percentage):
        if percentage >= 90:
            return 'A+'
        if percentage >= 85:
            return 'A'
        if percentage >= 80:
            return 'A-'
        if percentage >= 75:
            return 'B+'
        if percentage >= 70:
            return 'B'
        if percentage >= 65:
            return 'B-'
        if percentage >= 60:
            return 'C+'
        if percentage >= 55:
            return 'C'
        if percentage >= 50:
            return 'C-'
        if percentage >= 40:
            return 'D'
        return 'F'

    @staticmethod
    def _distribution_bucket(grade_value):
        value = str(grade_value or '').upper()
        if 'A' in value:
            return 'A'
        if 'B' in value:
            return 'B'
        if 'C' in value:
            return 'C'
        if 'D' in value:
            return 'D'
        if value == 'F':
            return 'F'
        return 'other'

    @staticmethod
    def _performance_label(percentage):
        if percentage >= 90:
            return 'Excellent'
        if percentage >= 80:
            return 'Good'
        if percentage >= 60:
            return 'Average'
        return 'Below Average'
    
    @action(detail=True)
    def assignments(self, request, pk=None):
        """Get all assignments for subjects the student is enrolled in"""
        student = self.get_object()
        enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
        assignments = Assignment.objects.filter(
            subject_id__in=enrolled_subject_ids,
            subject__semester__number=student.current_semester
        ).select_related('subject', 'created_by')
        return Response(
            StudentAssignmentSerializer(
                assignments,
                many=True,
                context={'student': student, 'request': request}
            ).data
        )
    
    @action(detail=True)
    def grades(self, request, pk=None):
        student = self.get_object()
        
        # 1. Get Assignment Grades
        assignment_grades = Grade.objects.filter(
            submission__student=student,
            submission__assignment__subject__semester__number=student.current_semester
        ).select_related(
            'submission', 'submission__assignment', 'submission__assignment__subject'
        )
        serialized_assignments = GradeSerializer(assignment_grades, many=True).data
        # Add a type field to distinguish
        for g in serialized_assignments:
            g['grade_type'] = 'assignment'
        
        # 2. Get Component Marks (Quizzes, Midterms, etc. from grading system)
        component_marks = StudentMark.objects.filter(
            student=student,
            component__subject__semester__number=student.current_semester
        ).select_related('component', 'component__subject')
        serialized_components = StudentMarkSerializer(component_marks, many=True).data
        # Add a type field to distinguish
        for m in serialized_components:
            m['grade_type'] = 'assessment'
            
        # Combine both
        combined_grades = serialized_assignments + serialized_components
        
        # Sort by date (newest first)
        combined_grades.sort(
            key=lambda x: x.get('graded_at') or x.get('created_at') or '', 
            reverse=True
        )
        
        return Response(combined_grades)

    @action(detail=True, url_path='academic-history')
    def academic_history(self, request, pk=None):
        """Provides a detailed academic breakdown including assignments, quizzes, and component marks."""
        student = self.get_object()
        
        # 1. Fetch Assignment Grades for current semester
        assignment_grades = Grade.objects.filter(
            submission__student=student,
            submission__assignment__subject__semester__number=student.current_semester
        ).select_related(
            'submission', 'submission__assignment', 'submission__assignment__subject'
        )
        
        # 2. Fetch Quiz Attempts (for detailed quiz history)
        quiz_attempts = QuizAttempt.objects.filter(
            student=student,
            quiz__subject__semester__number=student.current_semester
        ).select_related(
            'quiz', 'quiz__subject'
        )

        # 3. Fetch ALL Component Marks for this student
        component_marks = StudentMark.objects.filter(
            student=student,
            component__subject__semester__number=student.current_semester
        ).select_related('component', 'component__subject', 'component__linked_quiz')

        # Use a dictionary to track unique assessment entries by their source ID or title+subject
        # This helps in "calculating jointly" for each subject
        records = []
        history = {
            'assignments': [],
            'quizzes': [],
            'others': [],
            'full_history': []
        }

        # Track results per subject for joint calculation
        subject_buckets = defaultdict(lambda: {
            'items': [],
            'total_weightage': 0,
            'weighted_sum': 0
        })

        # To avoid double counting when we have both StudentMark and QuizAttempt
        processed_quiz_ids = set()
        
        # Helper to get grade value
        def get_grade_val(pct):
            return self._grade_value_from_percentage(pct)

        all_history_records = []

        # 1. Process Component Marks (Authoritative Grades)
        # We process these FIRST because they represent the finalized marks
        for mark in component_marks:
            comp = mark.component
            subject = comp.subject
            
            marks_obtained = float(mark.marks_obtained or 0)
            total_marks = float(comp.max_marks or 0)
            
            # Fallback chain for total_marks when component max_marks is 0:
            # 1. Try linked quiz's total_marks
            # 2. Try summing quiz question marks
            if total_marks == 0 and hasattr(comp, 'linked_quiz') and comp.linked_quiz:
                linked_quiz = comp.linked_quiz
                total_marks = float(linked_quiz.total_marks or 0)
                if total_marks == 0:
                    # Sum question marks as final fallback
                    # Sum question marks as final fallback
                    q_total = linked_quiz.questions.aggregate(total=Sum('marks'))['total']
                    total_marks = float(q_total or 0)
            
            # Calculate percentage: prefer the stored value, but recalculate if it's 0 and we have marks
            percentage = float(mark.percentage or 0)
            if percentage == 0 and marks_obtained > 0 and total_marks > 0:
                percentage = round((marks_obtained / total_marks) * 100, 2)
            
            weight = float(comp.weightage or 0)
            
            # Try to resolve assignment_id for frontend linking
            assignment_id = None
            if comp.component_type == 'assignment':
                
                a_obj = Assignment.objects.filter(title=comp.name, subject=subject).first()
                if a_obj:
                    assignment_id = str(a_obj.id)

            entry = {
                'id': str(mark.id),
                'assignment_id': assignment_id, # Added for frontend deduplication
                'title': comp.name,
                'subject_name': subject.name if subject else 'Unknown',
                'subject_code': subject.code if subject else 'N/A',
                'percentage': round(percentage, 2),
                'marks_obtained': marks_obtained,
                'total_marks': total_marks,
                'grade_value': get_grade_val(percentage),
                'date': mark.graded_at.isoformat() if mark.graded_at else mark.created_at.isoformat(),
                'type': comp.component_type,
                'category': comp.get_component_type_display() if hasattr(comp, 'get_component_type_display') else 'Assessment',
                'weightage': weight,
                'status': 'Graded'
            }

            if comp.component_type == 'quiz':
                history['quizzes'].append(entry)
                if hasattr(comp, 'linked_quiz') and comp.linked_quiz:
                    processed_quiz_ids.add(comp.linked_quiz.id)
            elif comp.component_type == 'assignment':
                history['assignments'].append(entry)
            else:
                history['others'].append(entry)

            records.append(entry)
            all_history_records.append(entry)
            if subject:
                subject_key = f"{subject.name}::{subject.code}"
                subject_buckets[subject_key]['items'].append(entry)
                subject_buckets[subject_key]['total_weightage'] += weight
                subject_buckets[subject_key]['weighted_sum'] += (percentage * weight / 100.0)

        # 2. Process Assignments (Grade model)
        # Only add if not already covered by a StudentMark
        for grade in assignment_grades:
            assignment = grade.submission.assignment if grade.submission else None
            if not assignment: continue
            
            # Simple heuristic: if we already have an assignment with this title in history, skip
            if any(h['title'] == assignment.title for h in history['assignments']):
                continue

            subject = assignment.subject
            total_marks = float(assignment.total_marks or 0)
            marks_obtained = float(grade.marks_obtained or 0)
            percentage = round((marks_obtained / total_marks) * 100, 2) if total_marks > 0 else 0
            
            entry = {
                'id': str(grade.id),
                'assignment_id': str(assignment.id), # Added for frontend deduplication
                'title': assignment.title,
                'subject_name': subject.name if subject else 'Unknown',
                'subject_code': subject.code if subject else 'N/A',
                'percentage': percentage,
                'marks_obtained': marks_obtained,
                'total_marks': total_marks,
                'grade_value': grade.grade_value,
                'date': grade.graded_at.isoformat() if grade.graded_at else None,
                'type': 'assignment',
                'category': 'Assignment',
                'status': 'Graded'
            }
            records.append(entry)
            all_history_records.append(entry)
            history['assignments'].append(entry)
            
            if subject:
                subject_key = f"{subject.name}::{subject.code}"
                subject_buckets[subject_key]['items'].append(entry)

        # 3. Process Quiz Attempts
        # Only add to 'records' (official stats) if the quiz is linked to a component (already handled).
        # Otherwise, only add to history['quizzes'] and history['full_history'] for reference.
        for attempt in quiz_attempts:
            quiz = attempt.quiz
            if not quiz:
                continue
                
            # If already processed via StudentMark, we don't need to add it again anywhere
            # as the StudentMark record is more authoritative.
            if quiz.id in processed_quiz_ids:
                continue
            
            subject = quiz.subject
            total_marks = float(quiz.total_marks or 0)
            marks_obtained = float(attempt.score or 0)
            percentage = round((marks_obtained / total_marks) * 100, 2) if total_marks > 0 else 0
            
            entry = {
                'id': str(attempt.id),
                'title': quiz.title,
                'subject_name': subject.name if subject else 'Unknown',
                'subject_code': subject.code if subject else 'N/A',
                'percentage': percentage,
                'marks_obtained': marks_obtained,
                'total_marks': total_marks,
                'grade_value': get_grade_val(percentage),
                'date': attempt.completed_at.isoformat() if attempt.completed_at else attempt.started_at.isoformat(),
                'status': attempt.status.title() if attempt.status else 'Unknown',
                'type': 'quiz',
                'category': 'Quiz (Practice)'
            }
            
            # They only appear in history tabs.
            all_history_records.append(entry)
            history['quizzes'].append(entry)
            
            # We still add it to full history for the "History" tab
            # but we won't count it in the summary stats.
            # (Wait, if the user wants 'full history' to include them, we keep them in history)

        # Finalize Full History (sorted by date)
        history['full_history'] = sorted(all_history_records, key=lambda x: x.get('date', '') or '', reverse=True)

        # Process Subject Performance (Joint Calculation)
        subject_performance = []
        for subject_key, bucket in subject_buckets.items():
            name, code = subject_key.split('::')
            items = bucket['items']
            total_items = len(items)
            
            # If weightage is available, use it for average, else simple average
            if bucket['total_weightage'] > 0:
                # Scale weighted sum to 100% if weightage isn't complete yet
                avg_score = (bucket['weighted_sum'] / bucket['total_weightage']) * 100
            else:
                avg_score = sum(i['percentage'] for i in items) / total_items if total_items else 0
            
            best_score = max((i['percentage'] for i in items), default=0)
            worst_score = min((i['percentage'] for i in items), default=0)

            if avg_score >= 90: perf_label, color = 'Excellent', 'success'
            elif avg_score >= 80: perf_label, color = 'Good', 'success'
            elif avg_score >= 60: perf_label, color = 'Average', 'warning'
            else: perf_label, color = 'Below Average', 'danger'

            # Calculate category-specific averages for the "Detailed Grades" table
            cat_avgs = {
                'assignments': 0,
                'quizzes': 0,
                'midterm': 0,
                'final': 0,
                'lab': 0,
                'project': 0
            }
            
            # Map of component_type to these frontend-expected keys
            type_map = {
                'assignment': 'assignments',
                'quiz': 'quizzes',
                'midterm': 'midterm',
                'final': 'final',
                'lab': 'lab',
                'project': 'project'
            }
            
            # Count and sum percentages for each category
            cat_counts = defaultdict(int)
            cat_sums = defaultdict(float)
            
            for i in items:
                cat_key = type_map.get(i.get('type'), 'others')
                cat_counts[cat_key] += 1
                cat_sums[cat_key] += i.get('percentage', 0)
            
            for key in cat_avgs:
                if cat_counts[key] > 0:
                    cat_avgs[key] = round(cat_sums[key] / cat_counts[key], 2)

            subject_performance.append({
                'name': name,
                'code': code,
                'count': total_items,
                'average': round(avg_score, 2),
                'best': round(best_score, 2),
                'worst': round(worst_score, 2),
                'performance': perf_label,
                'color': color,
                'rating': round(avg_score, 2),
                'total_weightage_graded': bucket['total_weightage'],
                'is_fully_graded': bucket['total_weightage'] >= 100,
                # Include category averages
                **cat_avgs
            })
        
        subject_performance.sort(key=lambda s: (s['name'], s['code']))

        # Overall Average (Joint Calculation across all records)
        total_grades = len(records)
        total_subjects = student.enrolled_subjects.count()
        average_score = round(sum(r['percentage'] for r in records) / total_grades, 2) if total_grades else 0
        gpa = round(sum(self._grade_point_from_percentage(r['percentage']) for r in records) / total_grades, 2) if total_grades else 0

        # Recalculate Distribution & Performance Summary
        distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0, 'other': 0}
        perf_counts = {'excellent': 0, 'good': 0, 'average': 0, 'below_average': 0}

        for record in records:
            pct = float(record['percentage'])
            distribution[self._distribution_bucket(record.get('grade_value'))] += 1
            if pct >= 90: perf_counts['excellent'] += 1
            elif pct >= 80: perf_counts['good'] += 1
            elif pct >= 60: perf_counts['average'] += 1
            else: perf_counts['below_average'] += 1

        total = total_grades or 1
        performance_summary = [
            {'label': 'Excellent', 'range': '90-100%', 'value': perf_counts['excellent'], 'percent': round((perf_counts['excellent'] / total) * 100, 2), 'color': 'success'},
            {'label': 'Good', 'range': '80-89%', 'value': perf_counts['good'], 'percent': round((perf_counts['good'] / total) * 100, 2), 'color': 'success', 'opacity': 'bg-opacity-75'},
            {'label': 'Average', 'range': '60-79%', 'value': perf_counts['average'], 'percent': round((perf_counts['average'] / total) * 100, 2), 'color': 'warning'},
            {'label': 'Below Average', 'range': '<60%', 'value': perf_counts['below_average'], 'percent': round((perf_counts['below_average'] / total) * 100, 2), 'color': 'danger'},
        ]

        return Response({
            'student': {
                'id': str(student.id),
                'full_name': student.full_name,
                'enrollment_number': student.enrollment_number,
            },
            'summary': {
                'overall_gpa': f"{gpa:.2f}",
                'average_score': average_score,
                'total_subjects': total_subjects,
                'total_grades': total_grades,
                'performance': self._performance_label(average_score),
            },
            'distribution': distribution,
            'performance_summary': performance_summary,
            'subject_performance': subject_performance,
            'history': history,
        })

    @action(detail=True)
    def enrollments(self, request, pk=None):
        student = self.get_object()
        
        # Default to only returning current semester subjects unless history=true is requested
        if request.query_params.get('history') == 'true':
            queryset = student.enrolled_subjects.all().select_related('subject', 'semester')
        else:
            queryset = self._current_enrollments(student).select_related('subject', 'semester')
        
        # Annotate with evidence counts to see if teacher has created anything to grade
        queryset = queryset.annotate(
            total_components=Count('subject__grade_components', distinct=True),
            total_assignments=Count('subject__assignments', distinct=True)
        )
        
        if request.query_params.get('current_only') == 'true':
            current_qs = self._current_enrollments(student).values_list('id', flat=True)
            queryset = queryset.filter(id__in=current_qs)
        return Response(StudentSubjectSerializer(queryset, many=True).data)
    
    @action(detail=True)
    def announcements(self, request, pk=None):
        """Get all announcements for subjects the student is enrolled in"""
        
        
        student = self.get_object()
        
        # Keep announcements scoped to the student's current semester enrollment.
        enrolled_subject_ids = self._current_enrollments(student).values_list('subject_id', flat=True)
        
        # Get announcements for those subjects + general announcements (no subject)
        announcements = Announcement.objects.filter(
            Q(subject_id__in=enrolled_subject_ids) | Q(subject__isnull=True),
            is_active=True
        ).select_related('subject', 'created_by').order_by('-created_at')
        
        return Response(AnnouncementSerializer(announcements, many=True).data)
    
    @action(detail=True)
    def fees(self, request, pk=None):
        return Response(FeeSerializer(self.get_object().fees.all(), many=True).data)

    @action(detail=True)
    def class_schedule(self, request, pk=None):
        student = self.get_object()
        enrolled_subject_ids = self._current_enrollments(student).values_list('subject_id', flat=True)
        timetable = Timetable.objects.filter(subject_id__in=enrolled_subject_ids, is_active=True).select_related('subject', 'teacher')
        return Response(TimetableSerializer(timetable, many=True).data)

    @action(detail=True)
    def exam_schedule(self, request, pk=None):
        student = self.get_object()
        enrolled_subject_ids = self._current_enrollments(student).values_list('subject_id', flat=True)
        exams = Exam.objects.filter(subject_id__in=enrolled_subject_ids).select_related('subject')
        return Response(ExamSerializer(exams, many=True).data)

    @action(detail=True)
    def attendance(self, request, pk=None):
        student = self.get_object()
        return Response(AttendanceSerializer(student.attendance_records.all(), many=True).data)
        
    @action(detail=True, url_path='grade-report')
    def grade_report(self, request, pk=None):
        """Alias for academic_history to satisfy frontend calls"""
        return self.academic_history(request, pk)


class TeacherViewSet(BaseProfileViewSet):
    queryset = Teacher.objects.select_related('department', 'department__institution').filter(
        department__isnull=False,
        department__is_active=True,
        department__institution__is_active=True
    )
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    search_fields = ['full_name', 'email', 'employee_id', 'phone', 'cnic', 
                    'qualification', 'specialization']
    filterset_fields = ['department', 'is_active', 'is_verified', 'is_suspended', 
                       'gender', 'designation']
    ordering_fields = ['full_name', 'created_at', 'employee_id', 'joining_date']

    def get_permissions(self):
        # Teachers can view teacher profiles, but only admins can create/update/delete.
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrTeacher]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        return TeacherDetailSerializer if self.action == 'retrieve' else TeacherSerializer
    
    @action(detail=True)
    def teaching_subjects(self, request, pk=None):
        return Response(TeacherSubjectSerializer(self.get_object().teaching_subjects.all(), many=True).data)
    
    @action(detail=True)
    def created_assignments(self, request, pk=None):
        return Response(AssignmentSerializer(self.get_object().created_assignments.all(), many=True).data)
    
    @action(detail=True)
    def graded_assignments(self, request, pk=None):
        return Response(GradeSerializer(self.get_object().graded_assignments.all(), many=True).data)
    
    @action(detail=True)
    def marked_attendance(self, request, pk=None):
        return Response(AttendanceSerializer(self.get_object().marked_attendance.all(), many=True).data)


class AdminViewSet(BaseProfileViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    search_fields = ['full_name', 'email', 'admin_id', 'phone', 'cnic']
    filterset_fields = ['is_active', 'is_verified', 'is_suspended', 
                       'gender', 'role', 'permissions_level']
    ordering_fields = ['full_name', 'created_at', 'admin_id']
    
    @action(detail=True)
    def created_events(self, request, pk=None):
        return Response(EventSerializer(self.get_object().created_events.all(), many=True).data)


class TeacherSubjectViewSet(BaseViewSet):
    queryset = TeacherSubject.objects.select_related(
        'teacher', 'teacher__department', 'teacher__department__institution',
        'subject', 'subject__semester', 'subject__semester__session', 'subject__semester__program',
        'subject__semester__program__department', 'subject__semester__program__department__institution'
    ).filter(
        teacher__department__is_active=True,
        teacher__department__institution__is_active=True,
        subject__semester__program__department__is_active=True,
        subject__semester__program__department__institution__is_active=True
    ).filter(Q(subject__semester__session__isnull=True) | Q(subject__semester__session__is_active=True))
    serializer_class = TeacherSubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_fields = ['teacher', 'subject', 'subject__semester', 'subject__semester__program']
    ordering_fields = ['teacher', 'subject']


class StudentSubjectViewSet(BaseViewSet):
    queryset = StudentSubject.objects.select_related(
        'student', 'student__program', 'student__program__department', 'student__program__department__institution', 'student__session',
        'subject', 'subject__semester', 'subject__semester__session', 'subject__semester__program',
        'subject__semester__program__department', 'subject__semester__program__department__institution',
        'semester', 'semester__session'
    ).filter(
        student__program__department__is_active=True,
        student__program__department__institution__is_active=True,
        subject__semester__program__department__is_active=True,
        subject__semester__program__department__institution__is_active=True
    ).filter(
        Q(student__session__isnull=True) | Q(student__session__is_active=True)
    ).filter(
        Q(subject__semester__session__isnull=True) | Q(subject__semester__session__is_active=True)
    )
    serializer_class = StudentSubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_fields = ['student', 'subject', 'semester', 'semester__program']
    ordering_fields = ['student', 'subject', 'enrollment_date']
    
    def perform_create(self, serializer):
        """Override create to automatically populate semester from subject if not provided"""
        
        
        # Get the subject from the request data
        subject = serializer.validated_data.get('subject')
        
        # If semester is not provided but subject is, get semester from subject
        if subject and not serializer.validated_data.get('semester'):
            if hasattr(subject, 'semester') and subject.semester:
                serializer.validated_data['semester'] = subject.semester
        
        try:
            serializer.save()
        except IntegrityError:
            # If duplicate exists, try to update the existing one with the semester
            student = serializer.validated_data.get('student')
            subject = serializer.validated_data.get('subject')
            semester = serializer.validated_data.get('semester')
            
            if student and subject:
                # Try to find and update existing enrollment
                existing = StudentSubject.objects.filter(
                    student=student, 
                    subject=subject
                ).first()
                
                if existing and semester and not existing.semester:
                    existing.semester = semester
                    existing.save()
                    # Return the updated instance
                    return existing
            
            # If we can't resolve it, raise the error
            raise
