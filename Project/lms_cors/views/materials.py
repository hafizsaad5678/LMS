from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, F


from .base import BaseViewSet
from ..models import Material, Announcement, ActivityLog, Teacher, TeacherSubject, StudentSubject
from ..serializers import MaterialSerializer, AnnouncementSerializer, ActivityLogSerializer
from ..permissions import IsTeacherUser, IsAdminUser, IsStudentUser


class MaterialViewSet(BaseViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]  # We handle specific role checks in get_queryset or override specific methods
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'material_type', 'uploaded_by', 'is_active']
    ordering_fields = ['uploaded_at', 'title', 'download_count']
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()

        # Teachers can see materials they uploaded OR for subjects they teach
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True
            ).values_list('subject', flat=True)
            return self.queryset.filter(
                Q(uploaded_by=teacher) | Q(subject__in=teacher_subjects),
                is_active=True
            ).distinct()
            
        # Students can see materials for subjects they are enrolled in (class_only) OR public materials
        elif hasattr(user, 'student_profile'):
            student = user.student_profile
            student_subjects = StudentSubject.objects.filter(
                student=student
            ).values_list('subject', flat=True)
            
            # Filter: (class_only AND in subject list) OR (public)
            qs = self.queryset.filter(
                Q(is_active=True),
                Q(access_level='public') | Q(access_level='class_only', subject__in=student_subjects)
            ).distinct()
            return qs
            
        return self.queryset.none()
    
    def perform_create(self, serializer):
        # Set the uploaded_by to current teacher
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(uploaded_by=self.request.user.teacher_profile)
            
            # Log activity
            ActivityLog.objects.create(
                user=self.request.user,
                user_type='teacher',
                action_type='upload',
                description=f"Uploaded material: {serializer.instance.title}",
                model_name='Material',
                object_id=str(serializer.instance.id)
            )

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        material = self.get_object()
        material.download_count = F('download_count') + 1
        material.save(update_fields=['download_count'])
        
        # Log activity
        user_type = 'admin'
        if hasattr(request.user, 'teacher_profile'):
            user_type = 'teacher'
        elif hasattr(request.user, 'student_profile'):
            user_type = 'student'
            
        ActivityLog.objects.create(
            user=request.user,
            user_type=user_type,
            action_type='download',
            description=f"Downloaded material: {material.title}",
            model_name='Material',
            object_id=str(material.id)
        )
        
        return Response({'status': 'count updated'})


class AnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]
    search_fields = ['title', 'message', 'subject__name', 'subject__code']
    filterset_fields = ['subject', 'priority', 'created_by', 'is_active']
    ordering_fields = ['created_at', 'title', 'priority', 'views']
    
    def get_queryset(self):
        # Teachers can only see announcements for subjects they teach
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True
            ).values_list('subject', flat=True)
            return self.queryset.filter(subject__in=teacher_subjects)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        # Set the created_by to current teacher
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(created_by=self.request.user.teacher_profile)
            
            # Log activity
            ActivityLog.objects.create(
                user=self.request.user,
                user_type='teacher',
                action_type='announcement',
                description=f"Created announcement: {serializer.instance.title}",
                model_name='Announcement',
                object_id=str(serializer.instance.id)
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    return Response({'message': 'pong', 'time': timezone.now()})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_materials(request):
    """
    Returns materials uploaded by the logged-in teacher OR for subjects they teach.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get teacher's subjects
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher, is_active=True
    ).values_list('subject', flat=True)
    
    # Teachers see materials they uploaded (even inactive ones) OR active materials for subjects they teach
    materials = Material.objects.filter(
        Q(uploaded_by=teacher) | (Q(subject__in=teacher_subjects) & Q(is_active=True))
    ).select_related('subject', 'uploaded_by').order_by('-uploaded_at').distinct()
    
    material_data = []
    for material in materials:
        material_data.append({
            'id': str(material.id),
            'title': material.title,
            'description': material.description,
            'subject_id': str(material.subject.id) if material.subject else None,
            'subject_name': material.subject.name if material.subject else 'N/A',
            'material_type': material.material_type,
            'file_upload': material.file_upload.url if material.file_upload else None,
            'file_url': material.file_url,
            'access_level': material.access_level,
            'file_size': material.file_size,
            'download_count': material.download_count,
            'uploaded_at': material.uploaded_at.isoformat(),
            'uploaded_by': material.uploaded_by.full_name if material.uploaded_by else 'Unknown'
        })
    
    return Response({'results': material_data, 'count': len(material_data)})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def teacher_announcements(request):
    """
    Returns announcements created by the logged-in teacher.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get teacher's subjects
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher, is_active=True
    ).values_list('subject', flat=True)
    
    # Get announcements for these subjects
    announcements = Announcement.objects.filter(
        subject__in=teacher_subjects,
        is_active=True
    ).select_related('subject', 'created_by').order_by('-created_at')
    
    announcement_data = []
    for announcement in announcements:
        announcement_data.append({
            'id': str(announcement.id),
            'title': announcement.title,
            'message': announcement.message,
            'subject_id': str(announcement.subject.id) if announcement.subject else None,
            'subject_name': announcement.subject.name if announcement.subject else 'N/A',
            'priority': announcement.priority,
            'views': announcement.views,
            'created_at': announcement.created_at.isoformat(),
            'created_by': announcement.created_by.full_name if announcement.created_by else 'Unknown'
        })
    
    return Response({'results': announcement_data, 'count': len(announcement_data)})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def create_material(request):
    """
    Create a new material.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MaterialSerializer(data=request.data)
    if serializer.is_valid():
        # Force active status on creation and include access_level
        access_level = request.data.get('access_level', 'class_only')
        serializer.save(
            uploaded_by=teacher, 
            is_active=True,
            access_level=access_level
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_type='teacher',
            action_type='upload',
            description=f"Uploaded {serializer.instance.material_type}: {serializer.instance.title}",
            model_name='Material',
            object_id=str(serializer.instance.id)
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherUser])
def create_announcement(request):
    """
    Create a new announcement.
    """
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return Response({'detail': 'Teacher profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AnnouncementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=teacher)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_type='teacher',
            action_type='announcement',
            description=f"Created announcement: {serializer.instance.title}",
            model_name='Announcement',
            object_id=str(serializer.instance.id)
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def activity_logs(request):
    """
    Returns activity logs for admin dashboard.
    """
    logs = ActivityLog.objects.all().select_related('user').order_by('-created_at')[:100]
    
    log_data = []
    for log in logs:
        log_data.append({
            'id': str(log.id),
            'username': log.user.username if log.user else 'Unknown',
            'user_type': log.user_type,
            'action_type': log.action_type,
            'description': log.description,
            'model_name': log.model_name,
            'created_at': log.created_at.isoformat(),
        })
    
    return Response({'results': log_data, 'count': len(log_data)})