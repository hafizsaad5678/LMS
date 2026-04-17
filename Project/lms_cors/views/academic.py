from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .base import BaseViewSet
from ..models import (
    Institution, Department, Program, AcademicSession, Semester, Subject,
    Student, Teacher, TeacherSubject
)
from ..serializers import (
    InstitutionSerializer, InstitutionDetailSerializer,
    DepartmentSerializer, DepartmentDetailSerializer,
    ProgramSerializer, ProgramDetailSerializer,
    AcademicSessionSerializer, AcademicSessionDetailSerializer,
    SemesterSerializer, SubjectSerializer, SubjectDetailSerializer,
    StudentSerializer, TeacherSerializer, TeacherSubjectSerializer, StudentSubjectSerializer
)
from ..services import SemesterFactory, EnrollmentService


class InstitutionViewSet(BaseViewSet):
    """ViewSet for Institution model."""
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    search_fields = ['name', 'short_name', 'code', 'email', 'city', 'country']
    filterset_fields = ['is_active', 'city', 'country', 'established_year']
    ordering_fields = ['name', 'code', 'established_year', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstitutionDetailSerializer
        return InstitutionSerializer
    
    @action(detail=True)
    def departments(self, request, pk=None):
        institution = self.get_object()
        departments = institution.departments.all()
        return Response(DepartmentSerializer(departments, many=True).data)
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        institution = self.get_object()
        from django.db.models import Count
        
        departments = institution.departments.all()
        dept_count = departments.count()
        total_teachers = Teacher.objects.filter(department__institution=institution).count()
        total_programs = Program.objects.filter(department__institution=institution).count()
        total_students = Student.objects.filter(program__department__institution=institution).count()
        
        return Response({
            'institution': institution.name,
            'code': institution.code,
            'total_departments': dept_count,
            'total_programs': total_programs,
            'total_teachers': total_teachers,
            'total_students': total_students,
        })
    
    @action(detail=False)
    def active(self, request):
        active_institutions = self.get_queryset().filter(is_active=True)
        return Response(self.get_serializer(active_institutions, many=True).data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        institution = self.get_object()
        institution.is_active = not institution.is_active
        institution.save()
        return Response({
            'id': str(institution.id),
            'name': institution.name,
            'is_active': institution.is_active
        })


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.select_related('institution').prefetch_related('programs', 'teachers').filter(
        institution__isnull=False,
        institution__is_active=True
    )
    serializer_class = DepartmentSerializer
    search_fields = ['name', 'code', 'description', 'head_of_department']
    filterset_fields = ['institution', 'is_active']
    ordering_fields = ['name', 'code', 'created_at']
    
    def get_serializer_class(self):
        return DepartmentDetailSerializer if self.action == 'retrieve' else DepartmentSerializer
    
    @action(detail=True)
    def programs(self, request, pk=None):
        return Response(ProgramSerializer(self.get_object().programs.all(), many=True).data)
    
    @action(detail=True)
    def teachers(self, request, pk=None):
        return Response(TeacherSerializer(self.get_object().teachers.all(), many=True).data)


class ProgramViewSet(BaseViewSet):
    queryset = Program.objects.select_related('department', 'department__institution').filter(
        department__isnull=False,
        department__is_active=True,
        department__institution__is_active=True
    )
    serializer_class = ProgramSerializer
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['department', 'program_level', 'academic_system']
    ordering_fields = ['name', 'code', 'duration_years']
    
    def get_serializer_class(self):
        return ProgramDetailSerializer if self.action == 'retrieve' else ProgramSerializer
    
    @action(detail=True)
    def semesters(self, request, pk=None):
        return Response(SemesterSerializer(self.get_object().semesters_legacy.all(), many=True).data)
    
    @action(detail=True)
    def students(self, request, pk=None):
        return Response(StudentSerializer(self.get_object().students_legacy.all(), many=True).data)
    
    @action(detail=True)
    def sessions(self, request, pk=None):
        return Response(AcademicSessionSerializer(self.get_object().sessions.all(), many=True).data)


class AcademicSessionViewSet(BaseViewSet):
    """ViewSet for Academic Session (Batch/Intake) management."""
    queryset = AcademicSession.objects.select_related('program', 'program__department', 'program__department__institution').filter(
        program__isnull=False,
        program__department__is_active=True,
        program__department__institution__is_active=True
    )
    serializer_class = AcademicSessionSerializer
    search_fields = ['session_name', 'session_code', 'program__name', 'program__code']
    filterset_fields = ['program', 'start_year', 'end_year', 'status', 'is_active', 
                       'program__department', 'program__program_level']
    ordering_fields = ['start_year', 'session_name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AcademicSessionDetailSerializer
        return AcademicSessionSerializer
    
    def perform_update(self, serializer):
        instance = serializer.save()
        instance.edit_count += 1
        instance.save(update_fields=['edit_count'])
    
    @action(detail=True)
    def semesters(self, request, pk=None):
        session = self.get_object()
        semesters = session.semesters.all().order_by('number')
        if not semesters.exists() and session.program:
            semesters = session.program.semesters_legacy.all().order_by('number')
        return Response(SemesterSerializer(semesters, many=True).data)
    
    @action(detail=True)
    def students(self, request, pk=None):
        session = self.get_object()
        students = session.students.all()
        if not students.exists() and session.program:
            students = session.program.students_legacy.all()
        return Response(StudentSerializer(students, many=True).data)
    
    @action(detail=True, methods=['post'])
    def setup_semesters(self, request, pk=None):
        session = self.get_object()
        if session.semesters.exists():
            return Response(
                {'error': f'Semesters already exist for {session.session_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            semesters = SemesterFactory.create_semesters_for_session(session)
            return Response({
                'message': f'Successfully created {len(semesters)} semesters for {session.session_name}',
                'semesters': SemesterSerializer(semesters, many=True).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to create semesters: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False)
    def active_sessions(self, request):
        active = self.get_queryset().filter(status='active', is_active=True)
        return Response(self.get_serializer(active, many=True).data)
    
    @action(detail=False)
    def upcoming_sessions(self, request):
        upcoming = self.get_queryset().filter(status='upcoming', is_active=True)
        return Response(self.get_serializer(upcoming, many=True).data)
    
    @action(detail=False)
    def program_sessions(self, request):
        program_id = request.query_params.get('program')
        if program_id:
            sessions = self.get_queryset().filter(program_id=program_id)
            return Response(self.get_serializer(sessions, many=True).data)
        return Response({'error': 'program parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        session = self.get_object()
        stats = EnrollmentService.calculate_enrollment_stats(session)
        stats.update({
            'session_name': session.session_name,
            'session_code': session.session_code,
            'program_name': session.program.name,
            'program_level': session.program.get_program_level_display() if session.program.program_level else 'N/A',
            'total_semesters': session.total_semesters,
            'semester_count': session.semesters.count(),
            'status': session.status
        })
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        session = self.get_object()
        session.status = 'active'
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        session = self.get_object()
        session.status = 'completed'
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        session = self.get_object()
        session.status = 'archived'
        session.is_active = False
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=False)
    def program_levels(self, request):
        levels = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Program.PROGRAM_LEVEL_CHOICES
        ]
        return Response(levels)


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.select_related('program', 'program__department', 'program__department__institution', 'session').filter(
        program__isnull=False,
        program__department__is_active=True,
        program__department__institution__is_active=True
    ).filter(Q(session__isnull=True) | Q(session__is_active=True))
    serializer_class = SemesterSerializer
    search_fields = ['name', 'program__name', 'program__code']
    filterset_fields = ['program', 'program__department']
    ordering_fields = ['number', 'name']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data.get('semesters', []), many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True)
    def subjects(self, request, pk=None):
        return Response(SubjectSerializer(self.get_object().subjects.all(), many=True).data)
    
    @action(detail=True)
    def student_enrollments(self, request, pk=None):
        return Response(StudentSubjectSerializer(self.get_object().student_enrollments.all(), many=True).data)


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.select_related('semester', 'semester__program', 'semester__session', 'semester__program__department', 'semester__program__department__institution').filter(
        semester__isnull=False,
        semester__program__department__is_active=True,
        semester__program__department__institution__is_active=True
    ).filter(Q(semester__session__isnull=True) | Q(semester__session__is_active=True))
    serializer_class = SubjectSerializer
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['semester', 'semester__program', 'semester__program__department']
    ordering_fields = ['code', 'name', 'credit_hours']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return SubjectSerializer
    
    @action(detail=True)
    def assignments(self, request, pk=None):
        from ..serializers import AssignmentSerializer
        return Response(AssignmentSerializer(self.get_object().assignments.all(), many=True).data)
    
    @action(detail=True)
    def enrolled_students(self, request, pk=None):
        return Response(StudentSubjectSerializer(self.get_object().enrolled_students.all(), many=True).data)
    
    @action(detail=True)
    def assigned_teachers(self, request, pk=None):
        return Response(TeacherSubjectSerializer(self.get_object().assigned_teachers.all(), many=True).data)
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        from ..serializers import AttendanceSerializer
        return Response(AttendanceSerializer(self.get_object().attendance_records.all(), many=True).data)
    
    @action(detail=False, methods=['get'])
    def available_subjects(self, request):
        active_assignments = TeacherSubject.objects.filter(is_active=True)
        exclude_teacher = request.query_params.get('exclude_teacher')
        if exclude_teacher:
            active_assignments = active_assignments.exclude(teacher_id=exclude_teacher)
        unavailable_subject_ids = active_assignments.values_list('subject_id', flat=True)
        available = Subject.objects.exclude(id__in=unavailable_subject_ids)
        semester = request.query_params.get('semester')
        if semester:
            available = available.filter(semester_id=semester)
        return Response(SubjectSerializer(available, many=True).data)

    @action(detail=False, methods=['get'])
    def assignment_status(self, request):
        active_assignments = TeacherSubject.objects.filter(is_active=True).select_related('teacher', 'subject')
        status_map = {}
        for assignment in active_assignments:
            status_map[str(assignment.subject.id)] = {
                'teacher_id': str(assignment.teacher.id),
                'teacher_name': assignment.teacher.full_name
            }
        return Response(status_map)
