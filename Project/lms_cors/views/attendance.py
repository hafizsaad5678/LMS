from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

from .base import BaseViewSet
from ..models import Attendance, Teacher, TeacherSubject
from ..serializers import AttendanceSerializer
from ..permissions import CanMarkAttendance


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, CanMarkAttendance]
    search_fields = ['student__full_name', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'student', 'status', 'marked_by', 
                       'session_date', 'subject__semester']
    ordering_fields = ['session_date', 'status', 'marked_at']
    ordering = ['-session_date', '-marked_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Attendance.objects.none()

        queryset = Attendance.objects.all()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            pass
        elif hasattr(user, 'teacher_profile'):
            # Teachers see attendance for subjects they teach
            teacher = user.teacher_profile
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True
            ).values_list('subject_id', flat=True)
            queryset = queryset.filter(subject_id__in=teacher_subjects)
        elif hasattr(user, 'student_profile'):
            # Students only see their own attendance
            queryset = queryset.filter(student=user.student_profile)
        else:
            return Attendance.objects.none()

        month = self.request.query_params.get('month')
        if month:
            try:
                queryset = queryset.filter(session_date__month=int(month))
            except (TypeError, ValueError):
                pass

        year = self.request.query_params.get('year')
        if year:
            try:
                queryset = queryset.filter(session_date__year=int(year))
            except (TypeError, ValueError):
                pass

        return queryset.distinct().order_by('-session_date', '-marked_at')
    
    def perform_create(self, serializer):
        """Automatically set marked_by to the current teacher"""
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(marked_by=teacher)
        except Teacher.DoesNotExist:
            # If user is not a teacher, save without marked_by
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple attendance records at once"""
        attendance_list = request.data if isinstance(request.data, list) else [request.data]
        
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({
                'error': 'Only teachers can mark attendance'
            }, status=status.HTTP_403_FORBIDDEN)
        
        created_records = []
        errors = []

        sample = next((item for item in attendance_list if isinstance(item, dict)), None)
        if sample:
            subject_id = sample.get('subject')
            session_date = sample.get('session_date')
            if subject_id and session_date:
                already_marked = Attendance.objects.filter(
                    subject_id=subject_id,
                    session_date=session_date
                ).exists()
                if already_marked:
                    return Response({
                        'warning': 'Attendance already marked for this subject and date.',
                        'created': 0,
                        'failed': 0,
                        'records': [],
                        'errors': []
                    }, status=status.HTTP_200_OK)
        
        for idx, attendance_data in enumerate(attendance_list):
            # Create a copy to avoid modifying the original
            data = attendance_data.copy() if isinstance(attendance_data, dict) else attendance_data
            
            # Set marked_by to current teacher
            data['marked_by'] = teacher.id
            
            try:
                # Check for existing record first
                existing = Attendance.objects.filter(
                    student_id=data.get('student'),
                    subject_id=data.get('subject'),
                    session_date=data.get('session_date')
                ).first()
                
                if existing:
                    errors.append({
                        'index': idx,
                        'data': data,
                        'error': 'Attendance already marked for this student and date.'
                    })
                else:
                    # Create new record
                    serializer = self.get_serializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        created_records.append(serializer.data)
                    else:
                        errors.append({
                            'index': idx,
                            'data': data,
                            'errors': serializer.errors
                        })
            except Exception as e:
                errors.append({
                    'index': idx,
                    'data': data,
                    'error': str(e)
                })
        
        return Response({
            'created': len(created_records),
            'failed': len(errors),
            'records': created_records,
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_records else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False)
    def today(self, request):
        today_records = self.get_queryset().filter(session_date=timezone.now().date())
        return Response(self.get_serializer(today_records, many=True).data)
