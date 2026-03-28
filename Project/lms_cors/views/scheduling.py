from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .base import BaseViewSet
from ..models import Event, Holiday, Exam, Timetable, TeacherSubject, StudentSubject, Teacher
from ..models.attendance import Attendance
from ..serializers import EventSerializer, HolidaySerializer, ExamSerializer, TimetableSerializer
from ..permissions import AdminFullAccess, ReadOnlyForStudents, IsTeacherUser


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, AdminFullAccess]
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


class HolidayViewSet(BaseViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, AdminFullAccess]
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
    permission_classes = [IsAuthenticated, ReadOnlyForStudents]
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
    permission_classes = [IsAuthenticated, ReadOnlyForStudents]
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


# Teacher-specific endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_timetable(request):
    """
    Returns the logged-in teacher's weekly timetable.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get teacher's timetable
    timetable_slots = Timetable.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject', 'subject__semester').order_by('day', 'start_time')
    
    schedule_data = []
    for slot in timetable_slots:
        # Count students in this class
        student_count = StudentSubject.objects.filter(subject=slot.subject).count() if slot.subject else 0
        
        schedule_data.append({
            'id': str(slot.id),
            'day': slot.day,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'subject': slot.subject.name if slot.subject else 'N/A',
            'subject_code': slot.subject.code if slot.subject else 'N/A',
            'room': slot.room,
            'students': student_count,
            'semester': f"Semester {slot.semester.number}" if slot.semester else 'N/A'
        })
    
    return Response({'results': schedule_data, 'count': len(schedule_data)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_exams(request):
    """
    Returns exams for subjects taught by the logged-in teacher.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get subjects taught by this teacher
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher, 
        is_active=True
    ).values_list('subject', flat=True)
    
    # Get exams for these subjects
    exams = Exam.objects.filter(
        subject__in=teacher_subjects
    ).select_related('subject', 'subject__semester').order_by('exam_date', 'exam_time')
    
    exam_data = []
    for exam in exams:
        # Count students enrolled in this subject
        student_count = StudentSubject.objects.filter(subject=exam.subject).count() if exam.subject else 0
        
        exam_data.append({
            'id': str(exam.id),
            'title': f"{exam.subject.name} {exam.exam_type.title()}" if exam.subject else f"{exam.exam_type.title()} Exam",
            'subject': f"{exam.subject.name} - {exam.subject.code}" if exam.subject else 'N/A',
            'type': exam.exam_type,
            'date': exam.exam_date.isoformat(),
            'time': exam.exam_time.strftime('%I:%M %p'),
            'duration': f"{exam.duration_minutes // 60}h {exam.duration_minutes % 60}m" if exam.duration_minutes >= 60 else f"{exam.duration_minutes}m",
            'venue': exam.room or 'TBA',
            'students': student_count,
            'total_marks': float(exam.total_marks),
            'status': exam.status,
            'phase': exam.phase
        })
    
    return Response({'results': exam_data, 'count': len(exam_data)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_attendance_report(request):
    """
    Returns attendance report for teacher's classes.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get subjects taught by this teacher
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher, 
        is_active=True
    ).values_list('subject', flat=True)
    
    # Get students enrolled in these subjects
    student_subjects = StudentSubject.objects.filter(
        subject__in=teacher_subjects
    ).select_related('student', 'subject')
    
    # Calculate attendance for each student
    attendance_data = []
    for ss in student_subjects:
        student = ss.student
        subject = ss.subject
        
        # Get attendance records for this student in this subject
        attendance_records = Attendance.objects.filter(
            student=student,
            subject=subject
        )
        
        total_classes = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        leave_count = attendance_records.filter(status='excused').count()
        
        percentage = round((present_count / total_classes * 100)) if total_classes > 0 else 0
        
        attendance_data.append({
            'id': str(student.id),
            'name': student.full_name,
            'roll_no': student.enrollment_number,
            'subject': subject.name,
            'present': present_count,
            'absent': absent_count,
            'leave': leave_count,
            'total_classes': total_classes,
            'percentage': percentage
        })
    
    return Response({'results': attendance_data, 'count': len(attendance_data)})
