from django.contrib import admin
from django.utils.html import format_html
from ..models import Fee, Expense, Account


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_type', 'amount', 'paid_amount', 'balance_display', 'due_date', 'status']
    list_filter = ['fee_type', 'status', 'due_date', 'semester']
    search_fields = ['student__full_name', 'student__enrollment_number', 'receipt_number']
    list_editable = ['status']
    ordering = ['-due_date']
    list_per_page = 20
    
    @admin.display(description='Balance')
    def balance_display(self, obj):
        balance = obj.balance
        color = 'red' if balance > 0 else 'green'
        return format_html('<span style="color: {};">PKR {}</span>', color, balance)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'expense_date', 'vendor', 'department', 'is_approved']
    list_filter = ['category', 'is_approved', 'expense_date', 'department']
    search_fields = ['title', 'description', 'vendor', 'receipt_number']
    list_editable = ['is_approved']
    ordering = ['-expense_date']
    list_per_page = 20


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'account_number', 'bank_name', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['name', 'account_number', 'bank_name']
    list_editable = ['is_active']
    ordering = ['name']
    list_per_page = 20
