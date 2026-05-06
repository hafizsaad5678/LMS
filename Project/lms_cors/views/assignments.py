from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from .base import BaseViewSet
from ..models import Assignment, SubmissionHistory, Grade, TeacherSubject, StudentSubject
from ..serializers import AssignmentSerializer, SubmissionHistorySerializer, GradeSerializer
from ..permissions import IsAdminOrTeacher, CanSubmitAssignment, CanGradeAssignments, ReadOnlyForStudents


class AssignmentViewSet(BaseViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForStudents]
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'created_by', 'subject__semester', 'subject__semester__program']
    ordering_fields = ['due_date', 'created_at', 'title']

    def _current_enrollments_for_student(self, student):
        queryset = StudentSubject.objects.filter(student=student)

        if getattr(student, 'session_id', None):
            queryset = queryset.filter(semester__session_id=student.session_id)

        if getattr(student, 'current_semester', None):
            queryset = queryset.filter(semester__number=student.current_semester)

        return queryset

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # If user is a teacher, restrict to subjects they teach
        if hasattr(user, 'teacher_profile') and not user.is_staff and not hasattr(user, 'admin_profile'):
            teacher = user.teacher_profile
            # Get subjects assigned to this teacher
            assigned_subjects = TeacherSubject.objects.filter(
                teacher=teacher, 
                is_active=True
            ).values_list('subject_id', flat=True)
            
            # Filter assignments either created by them OR belonging to their assigned subjects
            filtered_qs = qs.filter(Q(created_by=teacher) | Q(subject_id__in=assigned_subjects)).distinct()
            
            # If subject filter is provided, apply it
            subject_filter = self.request.GET.get('subject')
            if subject_filter:
                filtered_qs = filtered_qs.filter(subject_id=subject_filter)
            
            return filtered_qs
            
        # If user is a student, restrict to subjects they are enrolled in
        if hasattr(user, 'student_profile') and not user.is_staff and not hasattr(user, 'admin_profile'):
            student = user.student_profile
            enrolled_subject_ids = self._current_enrollments_for_student(student).values_list('subject_id', flat=True)
            return qs.filter(subject_id__in=enrolled_subject_ids)

        return qs

    def perform_create(self, serializer):
        # Automatically set created_by if the user is a teacher
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(created_by=self.request.user.teacher_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for this assignment"""
        assignment = self.get_object()
        
        # Verify teacher has access to this assignment's subject
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, 
                is_active=True
            ).values_list('subject_id', flat=True)
            
            # Check if teacher created this assignment OR teaches the subject
            if assignment.subject_id not in teacher_subjects and assignment.created_by != teacher:
                return Response(
                    {'detail': 'You do not have permission to view submissions for this assignment.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get all submissions for this assignment
        submissions = assignment.submissions.select_related(
            'student'
        ).prefetch_related('grade', 'grade__graded_by').all()
        
        serializer = SubmissionHistorySerializer(
            submissions, 
            many=True, 
            context={'request': request}
        )
        
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_zero(self, request, pk=None):
        """Allow teacher/admin to mark 0 when assignment is expired and student did not submit."""
        assignment = self.get_object()
        student_id = request.data.get('student') or request.data.get('student_id')

        if not student_id:
            return Response({'detail': 'student is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify teacher has access to this assignment's subject
        teacher = getattr(request.user, 'teacher_profile', None)
        if teacher:
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher,
                is_active=True
            ).values_list('subject_id', flat=True)

            if assignment.subject_id not in teacher_subjects and assignment.created_by != teacher:
                return Response({'detail': 'You do not have permission to grade this assignment.'}, status=status.HTTP_403_FORBIDDEN)

        if assignment.due_date and assignment.due_date > timezone.now():
            return Response({'detail': 'Cannot assign zero marks before due date expires.'}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = StudentSubject.objects.select_related('student').filter(
            student_id=student_id,
            subject=assignment.subject
        ).first()

        if not enrollment or not enrollment.student:
            return Response({'detail': 'Student is not enrolled in this assignment subject.'}, status=status.HTTP_404_NOT_FOUND)

        student = enrollment.student

        submission, _ = SubmissionHistory.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={
                'submission_text': 'No submission received before due date. Auto-marked by teacher.',
                'file_upload': None,
                'file_url': ''
            }
        )

        grade, created = Grade.objects.get_or_create(
            submission=submission,
            defaults={
                'grade_value': 'F',
                'marks_obtained': Decimal('0.00'),
                'feedback': 'Marked as 0 because no submission was received before due date.',
                'graded_by': teacher if teacher else None
            }
        )

        if not created:
            # Keep action idempotent and ensure explicit zero state.
            grade.grade_value = 'F'
            grade.marks_obtained = Decimal('0.00')
            if not grade.feedback:
                grade.feedback = 'Marked as 0 because no submission was received before due date.'
            if teacher:
                grade.graded_by = teacher
            grade.save()

        return Response({'detail': 'Zero marks assigned successfully.'}, status=status.HTTP_200_OK)


class SubmissionHistoryViewSet(BaseViewSet):
    queryset = SubmissionHistory.objects.all()
    serializer_class = SubmissionHistorySerializer
    permission_classes = [IsAuthenticated, CanSubmitAssignment]
    filterset_fields = ['assignment', 'student', 'assignment__subject']
    ordering_fields = ['submitted_at']
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # If student, only show their own submissions
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile).select_related(
                'student', 'assignment', 'assignment__subject'
            ).prefetch_related('grade', 'grade__graded_by').order_by('-submitted_at')
        
        # If teacher, show submissions for assignments they created OR in subjects they teach
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            # Get subjects the teacher teaches
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True
            ).values_list('subject_id', flat=True)
            # Return submissions for assignments created by teacher OR in their subjects
            return qs.filter(
                Q(assignment__created_by=teacher) | Q(assignment__subject_id__in=teacher_subjects)
            ).select_related(
                'student', 'assignment', 'assignment__subject'
            ).prefetch_related('grade', 'grade__graded_by').distinct().order_by('-submitted_at')
            
        return qs.select_related('student', 'assignment', 'assignment__subject').order_by('-submitted_at')
    
    def perform_create(self, serializer):
        """Bind submission ownership to authenticated student and validate assignment access."""
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise ValidationError('Only students can create submissions.')

        student = user.student_profile
        assignment = serializer.validated_data.get('assignment')
        if assignment is None:
            raise ValidationError({'assignment': 'This field is required.'})

        is_enrolled = StudentSubject.objects.filter(
            student=student,
            subject=assignment.subject
        ).exists()
        if not is_enrolled:
            raise ValidationError({'assignment': 'You are not enrolled in this assignment subject.'})

        serializer.save(student=student)
    
    @action(detail=True)
    def grade(self, request, pk=None):
        try:
            return Response(GradeSerializer(self.get_object().grade).data)
        except Grade.DoesNotExist:
            return Response({'detail': 'No grade yet'}, status=status.HTTP_404_NOT_FOUND)


class GradeViewSet(BaseViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, CanGradeAssignments]
    filterset_fields = ['submission__assignment', 'submission__student', 
                       'graded_by', 'grade_value', 'submission__assignment__subject']
    ordering_fields = ['graded_at', 'grade_value', 'marks_obtained']
    ordering = ['-graded_at']
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # If student, only show their own grades
        if hasattr(user, 'student_profile'):
            return qs.filter(submission__student=user.student_profile).order_by('-graded_at')

        return qs.order_by('-graded_at')
    
    def perform_create(self, serializer):
        # Automatically set graded_by if the user is a teacher
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(graded_by=self.request.user.teacher_profile)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        # Update graded_by if the user is a teacher
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(graded_by=self.request.user.teacher_profile)
        else:
            serializer.save()
