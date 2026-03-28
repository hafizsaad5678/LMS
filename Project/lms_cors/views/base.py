from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..permissions import AdminFullAccess


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common filter backends and default permissions"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticated, AdminFullAccess]


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
