from django.db import models
import uuid


class Fee(models.Model):
    """Student fee collection"""
    FEE_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partially Paid'),
        ('waived', 'Waived'),
    ]
    
    FEE_TYPES = [
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('exam', 'Exam Fee'),
        ('lab', 'Lab Fee'),
        ('library', 'Library Fee'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'lms_cors.Student', on_delete=models.CASCADE, 
        related_name='fees', null=True, blank=True
    )
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES, default='tuition')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FEE_STATUS, default='pending')
    semester = models.ForeignKey(
        'lms_cors.Semester', on_delete=models.CASCADE,
        related_name='fee_records', null=True, blank=True
    )
    receipt_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        db_table = 'fees'
        verbose_name = 'Fee Record'
        verbose_name_plural = 'Fee Records'
    
    def __str__(self):
        student = self.student.enrollment_number if self.student else "Unknown"
        return f"{student} - {self.fee_type} ({self.status})"
    
    @property
    def balance(self):
        return self.amount - self.paid_amount


class Expense(models.Model):
    """Institutional expense tracking"""
    EXPENSE_CATEGORIES = [
        ('salaries', 'Salaries & Wages'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('equipment', 'Equipment'),
        ('events', 'Events'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    vendor = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    approved_by = models.ForeignKey(
        'lms_cors.Admin', on_delete=models.SET_NULL, 
        related_name='approved_expenses', null=True, blank=True
    )
    department = models.ForeignKey(
        'lms_cors.Department', on_delete=models.SET_NULL,
        related_name='expenses', null=True, blank=True
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date']
        db_table = 'expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
    
    def __str__(self):
        return f"{self.title} - PKR {self.amount}"


class Account(models.Model):
    """Financial account management"""
    ACCOUNT_TYPES = [
        ('bank', 'Bank Account'),
        ('cash', 'Cash'),
        ('petty_cash', 'Petty Cash'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='bank')
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"{self.name} ({self.account_type})"
