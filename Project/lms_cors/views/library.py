from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal

from .base import BaseViewSet
from ..models import LibraryBook, LibraryBorrowPolicy, BookBorrowing
from ..serializers import LibraryBookSerializer, BookBorrowingSerializer, LibraryBorrowPolicySerializer
from ..permissions import ReadOnlyForStudents


class LibraryBookViewSet(BaseViewSet):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForStudents]
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
    permission_classes = [IsAuthenticated, ReadOnlyForStudents]
    filterset_fields = ['book', 'student', 'teacher', 'status']
    ordering_fields = ['borrowed_date', 'due_date']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def borrow_policy(self, request):
        policy = LibraryBorrowPolicy.get_active_policy()
        return Response(LibraryBorrowPolicySerializer(policy).data)
    
    def get_queryset(self):
        """Filter borrowings based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own borrowings
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_borrow(self, request):
        """Allow students to request borrowing a book"""
        from datetime import timedelta
        
        book_id = request.data.get('book')
        if not book_id:
            return Response({'error': 'Book ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = LibraryBook.objects.get(id=book_id)
        except LibraryBook.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if book.copies_available <= 0:
            return Response({'error': 'Book is not available'}, status=status.HTTP_400_BAD_REQUEST)

        policy = LibraryBorrowPolicy.get_active_policy()
        requested_days_raw = request.data.get('requested_days', policy.free_days)

        try:
            requested_days = int(requested_days_raw)
        except (TypeError, ValueError):
            return Response({'error': 'Requested days must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

        if requested_days < 1:
            return Response({'error': 'Requested days must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)

        if requested_days > policy.max_request_days:
            return Response({'error': f'Maximum allowed days are {policy.max_request_days}.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student already has this book borrowed
        if hasattr(request.user, 'student_profile'):
            existing = BookBorrowing.objects.filter(
                book=book,
                student=request.user.student_profile,
                status='borrowed'
            ).exists()
            
            if existing:
                return Response({'error': 'You already have this book borrowed'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Due date follows active policy free-days window.
            due_date = timezone.now().date() + timedelta(days=policy.free_days)
            borrowing = BookBorrowing.objects.create(
                book=book,
                student=request.user.student_profile,
                borrowed_date=timezone.now().date(),
                requested_days=requested_days,
                due_date=due_date,
                status='borrowed'
            )
            
            return Response(self.get_serializer(borrowing).data, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Only students can borrow books'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False)
    def overdue(self, request):
        overdue = self.get_queryset().filter(
            status='borrowed', due_date__lt=timezone.now().date()
        )
        return Response(self.get_serializer(overdue, many=True).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        
        # Students can only return their own books
        if hasattr(request.user, 'student_profile'):
            if borrowing.student != request.user.student_profile:
                return Response({'error': 'You can only return your own books'}, status=status.HTTP_403_FORBIDDEN)
        
        if borrowing.status == 'returned':
            return Response({'error': 'Book already returned'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status (model save method will handle availability increment)
        policy = LibraryBorrowPolicy.get_active_policy()
        borrowed_days = max((timezone.now().date() - borrowing.borrowed_date).days, 0)
        extra_days = max(borrowed_days - policy.free_days, 0)
        borrowing.fine_amount = Decimal(extra_days) * policy.fine_per_day
        borrowing.status = 'returned'
        borrowing.returned_date = timezone.now().date()
        borrowing.save()
        
        return Response(self.get_serializer(borrowing).data)
