from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum

from .base import BaseViewSet
from ..models import Fee, Expense, Account
from ..serializers import FeeSerializer, ExpenseSerializer, AccountSerializer
from ..permissions import IsAdminUser, AdminFullAccess


class FeeViewSet(BaseViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [IsAuthenticated, AdminFullAccess]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
        expenses = Expense.objects.filter(is_approved=True).values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        return Response(list(expenses))


class AccountViewSet(BaseViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    search_fields = ['name', 'account_number', 'bank_name']
    filterset_fields = ['account_type', 'is_active']
    ordering_fields = ['name', 'balance', 'created_at']
    
    @action(detail=False)
    def total_balance(self, request):
        total = Account.objects.filter(is_active=True).aggregate(Sum('balance'))['balance__sum'] or 0
        return Response({'total_balance': total})
