from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .base import BaseProfileViewSet, BaseViewSet
from ..models import (
    Student, Teacher, Admin, TeacherSubject, StudentSubject, 
    Grade, StudentMark, Assignment, SubmissionHistory
)
from ..serializers import (
    StudentSerializer, StudentDetailSerializer,
    TeacherSerializer, TeacherDetailSerializer,
    AdminSerializer,
    TeacherSubjectSerializer, StudentSubjectSerializer,
    SubmissionHistorySerializer, GradeSerializer, AttendanceSerializer,
    AssignmentSerializer, EventSerializer, FeeSerializer, StudentMarkSerializer
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

    # Get all TeacherSubject assignments for this teacher with related data
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher, 
        is_active=True
    ).select_related(
        'subject', 
        'subject__semester', 
        'subject__semester__session',
        'subject__semester__program',
        'subject__semester__program__department'
    )

    if session_id:
        teacher_subjects = teacher_subjects.filter(subject__semester__session_id=session_id)
    if subject_id:
        teacher_subjects = teacher_subjects.filter(subject_id=subject_id)
    
    # Build response data with full academic hierarchy
    classes = []
    for ts in teacher_subjects:
        subject = ts.subject
        if subject:
            semester = subject.semester
            session = semester.session if semester else None
            program = semester.program if semester else None
            department = program.department if program else None
            
            # Count enrolled students for this subject
            student_count = StudentSubject.objects.filter(subject=subject).count()
            
            classes.append({
                'id': str(ts.id),
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
    
    from django.db.models import Count, Q
    
    # Get assignments with submission counts using annotation (avoids N+1 queries)
    assignments = Assignment.objects.filter(
        created_by=teacher
    ).select_related(
        'subject', 'subject__semester'
    ).annotate(
        submission_count=Count('submissions'),
        total_students=Count('subject__enrolled_students', distinct=True)
    ).order_by('-created_at')
    
    assignment_data = []
    for assignment in assignments:
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
    
    # Verify teacher teaches this subject
    try:
        teacher_subject = TeacherSubject.objects.get(
            id=class_id, 
            teacher=teacher, 
            is_active=True
        )
    except TeacherSubject.DoesNotExist:
        return Response({'detail': 'Class not found or not assigned to you.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Optional filters
    session_id = request.query_params.get('session')

    # Get students enrolled in this subject
    student_subjects = StudentSubject.objects.filter(
        subject=teacher_subject.subject
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
            'subject_name': teacher_subject.subject.name,
            'subject_code': teacher_subject.subject.code,
            'semester': f"Semester {teacher_subject.subject.semester.number}" if teacher_subject.subject.semester else "N/A"
        }
    })


class StudentViewSet(BaseProfileViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, CanManageStudents]
    search_fields = ['full_name', 'email', 'enrollment_number', 'phone', 'cnic']
    filterset_fields = ['program', 'is_active', 'is_verified', 'is_suspended', 
                       'gender', 'enrollment_year', 'current_semester']
    ordering_fields = ['full_name', 'created_at', 'enrollment_number', 'enrollment_year']
    
    def get_serializer_class(self):
        return StudentDetailSerializer if self.action == 'retrieve' else StudentSerializer
    
    @action(detail=True)
    def submissions(self, request, pk=None):
        return Response(SubmissionHistorySerializer(self.get_object().submissions.all(), many=True).data)
    
    @action(detail=True)
    def assignments(self, request, pk=None):
        """Get all assignments for subjects the student is enrolled in"""
        student = self.get_object()
        # Get all subjects the student is enrolled in
        enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
        # Get assignments for those subjects
        from ..models import Assignment
        assignments = Assignment.objects.filter(subject_id__in=enrolled_subject_ids).select_related('subject', 'created_by')
        from ..serializers import StudentAssignmentSerializer
        return Response(StudentAssignmentSerializer(assignments, many=True, context={'student': student}).data)
    
    @action(detail=True)
    def grades(self, request, pk=None):
        student = self.get_object()
        
        # 1. Get Assignment Grades (linked via submission)
        assignment_grades = Grade.objects.filter(submission__student=student).select_related(
            'submission', 'submission__assignment', 'submission__assignment__subject'
        )
        serialized_assignments = GradeSerializer(assignment_grades, many=True).data
        # Add a type field to distinguish
        for g in serialized_assignments:
            g['grade_type'] = 'assignment'
        
        # 2. Get Component Marks (Quizzes, Midterms, etc. from grading system)
        # Only show if component is visible to students
        component_marks = StudentMark.objects.filter(
            student=student,
            component__is_visible_to_students=True
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
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        return Response(AttendanceSerializer(self.get_object().attendance_records.all(), many=True).data)
    
    @action(detail=True)
    def enrolled_subjects(self, request, pk=None):
        student = self.get_object()
        queryset = student.enrolled_subjects.all().select_related('subject', 'semester')
        if request.query_params.get('current_only') == 'true':
            if hasattr(student, 'current_semester_ref') and student.current_semester_ref:
                queryset = queryset.filter(semester=student.current_semester_ref)
        return Response(StudentSubjectSerializer(queryset, many=True).data)
    
    @action(detail=True)
    def announcements(self, request, pk=None):
        """Get all announcements for subjects the student is enrolled in"""
        from django.db.models import Q
        from ..models import Announcement
        from ..serializers import AnnouncementSerializer
        
        student = self.get_object()
        
        # Get all subjects the student is enrolled in
        enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
        
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
        enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
        from ..models import Timetable
        timetable = Timetable.objects.filter(subject_id__in=enrolled_subject_ids, is_active=True).select_related('subject', 'teacher')
        from ..serializers import TimetableSerializer
        return Response(TimetableSerializer(timetable, many=True).data)

    @action(detail=True)
    def exam_schedule(self, request, pk=None):
        student = self.get_object()
        enrolled_subject_ids = student.enrolled_subjects.values_list('subject_id', flat=True)
        from ..models import Exam
        exams = Exam.objects.filter(subject_id__in=enrolled_subject_ids).select_related('subject')
        from ..serializers import ExamSerializer
        return Response(ExamSerializer(exams, many=True).data)


class TeacherViewSet(BaseProfileViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    search_fields = ['full_name', 'email', 'employee_id', 'phone', 'cnic', 
                    'qualification', 'specialization']
    filterset_fields = ['department', 'is_active', 'is_verified', 'is_suspended', 
                       'gender', 'designation']
    ordering_fields = ['full_name', 'created_at', 'employee_id', 'joining_date']
    
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
    queryset = TeacherSubject.objects.all()
    serializer_class = TeacherSubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_fields = ['teacher', 'subject', 'subject__semester', 'subject__semester__program']
    ordering_fields = ['teacher', 'subject']


class StudentSubjectViewSet(BaseViewSet):
    queryset = StudentSubject.objects.all()
    serializer_class = StudentSubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_fields = ['student', 'subject', 'semester', 'semester__program']
    ordering_fields = ['student', 'subject', 'enrollment_date']
    
    def perform_create(self, serializer):
        """Override create to automatically populate semester from subject if not provided"""
        from django.db import IntegrityError
        
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
