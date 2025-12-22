from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum

from .models import (
    Institution, Department, Program, AcademicSession, Semester, Subject,
    Student, Teacher, TeacherSubject, StudentSubject,
    Assignment, SubmissionHistory, Grade, Attendance,
    Admin, Event, Holiday, Exam, Timetable,
    Fee, Expense, Account, LibraryBook, BookBorrowing
)
from .serializers import (
    InstitutionSerializer, InstitutionDetailSerializer,
    DepartmentSerializer, ProgramSerializer, AcademicSessionSerializer,
    AcademicSessionDetailSerializer, SemesterSerializer, SubjectSerializer,
    StudentSerializer, TeacherSerializer, TeacherSubjectSerializer, StudentSubjectSerializer,
    AssignmentSerializer, SubmissionHistorySerializer, GradeSerializer, AttendanceSerializer,
    AdminSerializer, EventSerializer,
    DepartmentDetailSerializer, ProgramDetailSerializer, 
    StudentDetailSerializer, TeacherDetailSerializer,
    HolidaySerializer, ExamSerializer, TimetableSerializer,
    FeeSerializer, ExpenseSerializer, AccountSerializer,
    LibraryBookSerializer, BookBorrowingSerializer
)
from .services import SemesterFactory, EnrollmentService


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common filter backends"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


class BaseProfileViewSet(BaseViewSet):
    """Base ViewSet for profile models (Student, Teacher, Admin)"""
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        obj.activate()
        return Response(self.get_serializer(obj).data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        obj = self.get_object()
        obj.deactivate()
        return Response(self.get_serializer(obj).data)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        obj = self.get_object()
        obj.suspend(request.data.get('reason', ''))
        return Response(self.get_serializer(obj).data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        obj = self.get_object()
        obj.verify()
        return Response(self.get_serializer(obj).data)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'new_password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        obj = self.get_object()
        if obj.reset_password(new_password):
            return Response({'status': 'password reset successful'})
        return Response({'error': 'Password reset failed'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def create_user_account(self, request, pk=None):
        obj = self.get_object()
        created, user = obj.create_user_account(request.data.get('password'))
        if user:
            return Response({
                'status': 'created' if created else 'already_exists',
                'user_id': user.id,
                'username': user.username
            })
        return Response({'error': 'Failed to create user account'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False)
    def active(self, request):
        return Response(self.get_serializer(
            self.get_queryset().filter(is_active=True), many=True
        ).data)
    
    @action(detail=False)
    def suspended(self, request):
        return Response(self.get_serializer(
            self.get_queryset().filter(is_suspended=True), many=True
        ).data)
    
    @action(detail=False)
    def verified(self, request):
        return Response(self.get_serializer(
            self.get_queryset().filter(is_verified=True), many=True
        ).data)


# ==================== ACADEMIC STRUCTURE ====================

class InstitutionViewSet(BaseViewSet):
    """
    ViewSet for Institution model.
    Provides CRUD operations and custom actions for institution management.
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    search_fields = ['name', 'short_name', 'code', 'email', 'city', 'country']
    filterset_fields = ['is_active', 'city', 'country', 'established_year']
    ordering_fields = ['name', 'code', 'established_year', 'created_at']
    
    def get_serializer_class(self):
        """Return detail serializer for retrieve action"""
        if self.action == 'retrieve':
            return InstitutionDetailSerializer
        return InstitutionSerializer
    
    @action(detail=True)
    def departments(self, request, pk=None):
        """Get all departments for this institution"""
        institution = self.get_object()
        departments = institution.departments.all()
        return Response(DepartmentSerializer(departments, many=True).data)
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        """Get statistics for this institution using optimized queries"""
        institution = self.get_object()
        
        # Use aggregation instead of nested loops for better performance
        from django.db.models import Count
        
        departments = institution.departments.all()
        dept_count = departments.count()
        
        # Count teachers directly
        total_teachers = Teacher.objects.filter(department__institution=institution).count()
        
        # Count programs and students using aggregation
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
        """Get all active institutions"""
        active_institutions = self.get_queryset().filter(is_active=True)
        return Response(self.get_serializer(active_institutions, many=True).data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle institution active status"""
        institution = self.get_object()
        institution.is_active = not institution.is_active
        institution.save()
        return Response({
            'id': str(institution.id),
            'name': institution.name,
            'is_active': institution.is_active
        })


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
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
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['department', 'program_level', 'academic_system']
    ordering_fields = ['name', 'code', 'duration_years']
    
    def get_serializer_class(self):
        return ProgramDetailSerializer if self.action == 'retrieve' else ProgramSerializer
    
    @action(detail=True)
    def semesters(self, request, pk=None):
        # Return both legacy semesters and session-based semesters
        return Response(SemesterSerializer(self.get_object().semesters_legacy.all(), many=True).data)
    
    @action(detail=True)
    def students(self, request, pk=None):
        return Response(StudentSerializer(self.get_object().students_legacy.all(), many=True).data)
    
    @action(detail=True)
    def sessions(self, request, pk=None):
        """Get all sessions for this program"""
        return Response(AcademicSessionSerializer(self.get_object().sessions.all(), many=True).data)


class AcademicSessionViewSet(BaseViewSet):
    """
    ViewSet for Academic Session (Batch/Intake) management.
    Provides CRUD operations and custom actions for session management.
    """
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    search_fields = ['session_name', 'session_code', 'program__name', 'program__code']
    filterset_fields = ['program', 'start_year', 'end_year', 'status', 'is_active', 
                       'program__department', 'program__program_level']
    ordering_fields = ['start_year', 'session_name', 'created_at']
    
    def get_serializer_class(self):
        """Return detail serializer for retrieve action"""
        if self.action == 'retrieve':
            return AcademicSessionDetailSerializer
        return AcademicSessionSerializer
    
    def perform_update(self, serializer):
        """Increment edit count when session is updated"""
        instance = serializer.save()
        instance.edit_count += 1
        instance.save(update_fields=['edit_count'])
    
    @action(detail=True)
    def semesters(self, request, pk=None):
        """Get all semesters for this session (or from program if not linked)"""
        session = self.get_object()
        # First try session-linked semesters
        semesters = session.semesters.all().order_by('number')
        # Fallback to program-linked semesters if none found
        if not semesters.exists() and session.program:
            semesters = session.program.semesters_legacy.all().order_by('number')
        return Response(SemesterSerializer(semesters, many=True).data)
    
    @action(detail=True)
    def students(self, request, pk=None):
        """Get all students enrolled in this session (or from program if not linked)"""
        session = self.get_object()
        # First try session-linked students
        students = session.students.all()
        # Fallback to program-linked students if none found
        if not students.exists() and session.program:
            students = session.program.students_legacy.all()
        return Response(StudentSerializer(students, many=True).data)
    
    @action(detail=True, methods=['post'])
    def setup_semesters(self, request, pk=None):
        """
        Auto-create semesters for this session based on program type
        Uses SemesterFactory service
        """
        session = self.get_object()
        
        # Check if semesters already exist
        if session.semesters.exists():
            return Response(
                {'error': f'Semesters already exist for {session.session_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use SemesterFactory to create semesters
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
        """Get all active sessions"""
        active = self.get_queryset().filter(status='active', is_active=True)
        return Response(self.get_serializer(active, many=True).data)
    
    @action(detail=False)
    def upcoming_sessions(self, request):
        """Get all upcoming sessions"""
        upcoming = self.get_queryset().filter(status='upcoming', is_active=True)
        return Response(self.get_serializer(upcoming, many=True).data)
    
    @action(detail=False)
    def program_sessions(self, request):
        """Get sessions filtered by program ID"""
        program_id = request.query_params.get('program')
        if program_id:
            sessions = self.get_queryset().filter(program_id=program_id)
            return Response(self.get_serializer(sessions, many=True).data)
        return Response(
            {'error': 'program parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        """Get statistics for this session"""
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
        """Activate a session"""
        session = self.get_object()
        session.status = 'active'
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark session as completed"""
        session = self.get_object()
        session.status = 'completed'
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a session"""
        session = self.get_object()
        session.status = 'archived'
        session.is_active = False
        session.save()
        return Response(self.get_serializer(session).data)
    
    @action(detail=False)
    def program_levels(self, request):
        """Get available program levels"""
        from .models import Program
        levels = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Program.PROGRAM_LEVEL_CHOICES
        ]
        return Response(levels)


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    search_fields = ['name', 'program__name', 'program__code']
    filterset_fields = ['program', 'program__department']
    ordering_fields = ['number', 'name']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create semesters.
        Expected payload:
        {
            "semesters": [
                {"program": id, "number": 1, ...},
                ...
            ]
        }
        """
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
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['semester', 'semester__program', 'semester__program__department']
    ordering_fields = ['code', 'name', 'credit_hours']
    
    @action(detail=True)
    def assignments(self, request, pk=None):
        return Response(AssignmentSerializer(self.get_object().assignments.all(), many=True).data)
    
    @action(detail=True)
    def enrolled_students(self, request, pk=None):
        return Response(StudentSubjectSerializer(self.get_object().enrolled_students.all(), many=True).data)
    
    @action(detail=True)
    def assigned_teachers(self, request, pk=None):
        return Response(TeacherSubjectSerializer(self.get_object().assigned_teachers.all(), many=True).data)
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        return Response(AttendanceSerializer(self.get_object().attendance_records.all(), many=True).data)
    
    @action(detail=False, methods=['get'])
    def available_subjects(self, request):
        """Get subjects that are not currently assigned to any active teacher"""
        # Get active assignments query
        active_assignments = TeacherSubject.objects.filter(is_active=True)
        
        # If excluding a specific teacher (e.g., when editing that teacher), allow their subjects
        exclude_teacher = request.query_params.get('exclude_teacher')
        if exclude_teacher:
            active_assignments = active_assignments.exclude(teacher_id=exclude_teacher)
            
        # Get IDs of subjects assigned to OTHER teachers
        unavailable_subject_ids = active_assignments.values_list('subject_id', flat=True)
        
        # Get subjects that are NOT in the unavailable list
        available = Subject.objects.exclude(id__in=unavailable_subject_ids)
        
        # Apply any filters from query params
        semester = request.query_params.get('semester')
        if semester:
            available = available.filter(semester_id=semester)
        
        return Response(SubjectSerializer(available, many=True).data)

    @action(detail=False, methods=['get'])
    def assignment_status(self, request):
        """Get mapping of subject_id -> assigned_teacher_name for all active assignments"""
        active_assignments = TeacherSubject.objects.filter(is_active=True).select_related('teacher', 'subject')
        
        status_map = {}
        for assignment in active_assignments:
            status_map[str(assignment.subject.id)] = {
                'teacher_id': str(assignment.teacher.id),
                'teacher_name': assignment.teacher.full_name
            }
            
        return Response(status_map)



# ==================== PEOPLE ====================

class StudentViewSet(BaseProfileViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
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
    def grades(self, request, pk=None):
        grades = Grade.objects.filter(submission__student=self.get_object())
        return Response(GradeSerializer(grades, many=True).data)
    
    @action(detail=True)
    def attendance(self, request, pk=None):
        return Response(AttendanceSerializer(self.get_object().attendance_records.all(), many=True).data)
    
    @action(detail=True)
    def enrolled_subjects(self, request, pk=None):
        student = self.get_object()
        queryset = student.enrolled_subjects.all().select_related('subject', 'semester')
        
        # Filter by current semester if requested
        if request.query_params.get('current_only') == 'true':
            if student.current_semester_ref:
                queryset = queryset.filter(semester=student.current_semester_ref)
        
        return Response(StudentSubjectSerializer(queryset, many=True).data)
    
    @action(detail=True)
    def fees(self, request, pk=None):
        return Response(FeeSerializer(self.get_object().fees.all(), many=True).data)


class TeacherViewSet(BaseProfileViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
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
    
    @action(detail=True)
    def salary_records(self, request, pk=None):
        return Response(SalarySerializer(self.get_object().salary_records.all(), many=True).data)


class AdminViewSet(BaseProfileViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    search_fields = ['full_name', 'email', 'admin_id', 'phone', 'cnic']
    filterset_fields = ['is_active', 'is_verified', 'is_suspended', 
                       'gender', 'role', 'permissions_level']
    ordering_fields = ['full_name', 'created_at', 'admin_id']
    
    @action(detail=True)
    def created_events(self, request, pk=None):
        return Response(EventSerializer(self.get_object().created_events.all(), many=True).data)


# ==================== JUNCTION TABLES ====================

class TeacherSubjectViewSet(BaseViewSet):
    queryset = TeacherSubject.objects.all()
    serializer_class = TeacherSubjectSerializer
    filterset_fields = ['teacher', 'subject', 'subject__semester', 'subject__semester__program']
    ordering_fields = ['teacher', 'subject']


class StudentSubjectViewSet(BaseViewSet):
    queryset = StudentSubject.objects.all()
    serializer_class = StudentSubjectSerializer
    filterset_fields = ['student', 'subject', 'semester', 'semester__program']
    ordering_fields = ['student', 'subject', 'enrollment_date']


# ==================== ACADEMIC MANAGEMENT ====================

class AssignmentViewSet(BaseViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'created_by', 'subject__semester', 'subject__semester__program']
    ordering_fields = ['due_date', 'created_at', 'title']
    
    @action(detail=True)
    def submissions(self, request, pk=None):
        return Response(SubmissionHistorySerializer(self.get_object().submissions.all(), many=True).data)


class SubmissionHistoryViewSet(BaseViewSet):
    queryset = SubmissionHistory.objects.all()
    serializer_class = SubmissionHistorySerializer
    filterset_fields = ['assignment', 'student', 'assignment__subject']
    ordering_fields = ['submitted_at']
    
    @action(detail=True)
    def grade(self, request, pk=None):
        try:
            return Response(GradeSerializer(self.get_object().grade).data)
        except Grade.DoesNotExist:
            return Response({'detail': 'No grade yet'}, status=status.HTTP_404_NOT_FOUND)


class GradeViewSet(BaseViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filterset_fields = ['submission__assignment', 'submission__student', 
                       'graded_by', 'grade_value', 'submission__assignment__subject']
    ordering_fields = ['graded_at', 'grade_value', 'marks_obtained']


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    search_fields = ['student__full_name', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'student', 'status', 'marked_by', 
                       'session_date', 'subject__semester']
    ordering_fields = ['session_date', 'status']
    
    @action(detail=False)
    def today(self, request):
        today_records = self.get_queryset().filter(session_date=timezone.now().date())
        return Response(self.get_serializer(today_records, many=True).data)


# ==================== ADMINISTRATION ====================

class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    search_fields = ['title', 'description', 'event_type', 'location']
    filterset_fields = ['event_type', 'created_by', 'event_date', 'is_active']
    ordering_fields = ['event_date', 'created_at']
    
    @action(detail=False)
    def upcoming(self, request):
        upcoming = self.get_queryset().filter(event_date__gte=timezone.now().date())
        return Response(self.get_serializer(upcoming, many=True).data)
    
    @action(detail=False)
    def past(self, request):
        past = self.get_queryset().filter(event_date__lt=timezone.now().date())
        return Response(self.get_serializer(past, many=True).data)
    
    @action(detail=False)
    def this_month(self, request):
        now = timezone.now()
        start = now.replace(day=1).date()
        end = (start.replace(day=28) + timezone.timedelta(days=4)).replace(day=1)
        events = self.get_queryset().filter(event_date__gte=start, event_date__lt=end)
        return Response(self.get_serializer(events, many=True).data)


# ==================== ACADEMIC SCHEDULING ====================

class HolidayViewSet(BaseViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    search_fields = ['name', 'description']
    filterset_fields = ['holiday_type', 'is_active', 'start_date']
    ordering_fields = ['start_date', 'created_at']
    
    @action(detail=False)
    def upcoming(self, request):
        upcoming = self.get_queryset().filter(start_date__gte=timezone.now().date())
        return Response(self.get_serializer(upcoming, many=True).data)
    
    @action(detail=False)
    def this_year(self, request):
        year = timezone.now().year
        holidays = self.get_queryset().filter(start_date__year=year)
        return Response(self.get_serializer(holidays, many=True).data)


class ExamViewSet(BaseViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    search_fields = ['subject__name', 'subject__code', 'room']
    filterset_fields = ['subject', 'exam_type', 'status', 'exam_date', 'subject__semester']
    ordering_fields = ['exam_date', 'exam_time', 'created_at']
    
    @action(detail=False)
    def upcoming(self, request):
        upcoming = self.get_queryset().filter(exam_date__gte=timezone.now().date(), status='scheduled')
        return Response(self.get_serializer(upcoming, many=True).data)
    
    @action(detail=False)
    def today(self, request):
        today = self.get_queryset().filter(exam_date=timezone.now().date())
        return Response(self.get_serializer(today, many=True).data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        exam = self.get_object()
        exam.status = 'completed'
        exam.save()
        return Response(self.get_serializer(exam).data)


class TimetableViewSet(BaseViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    search_fields = ['subject__name', 'subject__code', 'teacher__full_name', 'room']
    filterset_fields = ['day', 'subject', 'teacher', 'program', 'semester', 'room', 'is_active']
    ordering_fields = ['day', 'start_time']
    
    @action(detail=False)
    def by_day(self, request):
        day = request.query_params.get('day', 'monday')
        slots = self.get_queryset().filter(day=day.lower(), is_active=True)
        return Response(self.get_serializer(slots, many=True).data)
    
    @action(detail=False)
    def by_teacher(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id:
            slots = self.get_queryset().filter(teacher_id=teacher_id, is_active=True)
            return Response(self.get_serializer(slots, many=True).data)
        return Response({'error': 'teacher_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False)
    def by_room(self, request):
        room = request.query_params.get('room')
        if room:
            slots = self.get_queryset().filter(room=room, is_active=True)
            return Response(self.get_serializer(slots, many=True).data)
        return Response({'error': 'room required'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== MANAGEMENT/FINANCIAL ====================

class FeeViewSet(BaseViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    search_fields = ['student__full_name', 'student__enrollment_number', 'receipt_number']
    filterset_fields = ['student', 'fee_type', 'status', 'semester', 'due_date']
    ordering_fields = ['due_date', 'amount', 'created_at']
    
    @action(detail=False)
    def pending(self, request):
        pending = self.get_queryset().filter(status='pending')
        return Response(self.get_serializer(pending, many=True).data)
    
    @action(detail=False)
    def overdue(self, request):
        overdue = self.get_queryset().filter(status='overdue')
        # Also check pending fees past due date
        pending_overdue = self.get_queryset().filter(
            status='pending', due_date__lt=timezone.now().date()
        )
        combined = overdue | pending_overdue
        return Response(self.get_serializer(combined.distinct(), many=True).data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        fee = self.get_object()
        fee.status = 'paid'
        fee.paid_amount = fee.amount
        fee.payment_date = timezone.now().date()
        fee.save()
        return Response(self.get_serializer(fee).data)
    
    @action(detail=False)
    def statistics(self, request):
        total_collected = Fee.objects.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        total_pending = Fee.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        overdue_count = Fee.objects.filter(status='overdue').count()
        return Response({
            'total_collected': total_collected,
            'total_pending': total_pending,
            'overdue_count': overdue_count
        })


class ExpenseViewSet(BaseViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    search_fields = ['title', 'description', 'vendor', 'receipt_number']
    filterset_fields = ['category', 'is_approved', 'department', 'expense_date']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expense = self.get_object()
        expense.is_approved = True
        expense.approved_by_id = request.data.get('admin_id')
        expense.save()
        return Response(self.get_serializer(expense).data)
    
    @action(detail=False)
    def pending_approval(self, request):
        pending = self.get_queryset().filter(is_approved=False)
        return Response(self.get_serializer(pending, many=True).data)
    
    @action(detail=False)
    def by_category(self, request):
        from django.db.models import Sum
        expenses = Expense.objects.filter(is_approved=True).values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        return Response(list(expenses))





class AccountViewSet(BaseViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    search_fields = ['name', 'account_number', 'bank_name']
    filterset_fields = ['account_type', 'is_active']
    ordering_fields = ['name', 'balance', 'created_at']
    
    @action(detail=False)
    def total_balance(self, request):
        total = Account.objects.filter(is_active=True).aggregate(Sum('balance'))['balance__sum'] or 0
        return Response({'total_balance': total})


class LibraryBookViewSet(BaseViewSet):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    search_fields = ['title', 'author', 'isbn', 'publisher', 'category']
    filterset_fields = ['status', 'category', 'publication_year']
    ordering_fields = ['title', 'author', 'created_at']
    
    @action(detail=False)
    def available(self, request):
        available = self.get_queryset().filter(copies_available__gt=0)
        return Response(self.get_serializer(available, many=True).data)
    
    @action(detail=True)
    def borrowings(self, request, pk=None):
        return Response(BookBorrowingSerializer(self.get_object().borrowings.all(), many=True).data)


class BookBorrowingViewSet(BaseViewSet):
    queryset = BookBorrowing.objects.all()
    serializer_class = BookBorrowingSerializer
    filterset_fields = ['book', 'student', 'teacher', 'status']
    ordering_fields = ['borrowed_date', 'due_date']
    
    @action(detail=False)
    def overdue(self, request):
        overdue = self.get_queryset().filter(
            status='borrowed', due_date__lt=timezone.now().date()
        )
        return Response(self.get_serializer(overdue, many=True).data)
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        borrowing.status = 'returned'
        borrowing.returned_date = timezone.now().date()
        borrowing.save()
        return Response(self.get_serializer(borrowing).data)