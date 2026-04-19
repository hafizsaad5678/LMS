from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError
import uuid


class LibraryBook(models.Model):
    """Library book management"""
    BOOK_STATUS = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    location = models.CharField(max_length=50, blank=True)  # Shelf/Row
    status = models.CharField(max_length=20, choices=BOOK_STATUS, default='available')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        db_table = 'library_books'
        verbose_name = 'Library Book'
        verbose_name_plural = 'Library Books'
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class LibraryBorrowPolicy(models.Model):
    """Admin-configurable borrowing and fine rules."""

    name = models.CharField(max_length=100, default='Default Policy')
    free_days = models.PositiveSmallIntegerField(default=5)
    fine_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'))
    max_request_days = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'library_borrow_policies'
        verbose_name = 'Library Borrow Policy'
        verbose_name_plural = 'Library Borrow Policies'

    def __str__(self):
        return f"{self.name} (Free: {self.free_days} days, Fine: Rs. {self.fine_per_day}/day)"

    def clean(self):
        if self.free_days < 1:
            raise ValidationError('Free days must be at least 1.')
        if self.max_request_days < self.free_days:
            raise ValidationError('Maximum request days must be greater than or equal to free days.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        if self.is_active:
            LibraryBorrowPolicy.objects.exclude(pk=self.pk).update(is_active=False)

    @classmethod
    def get_active_policy(cls):
        policy = cls.objects.filter(is_active=True).first()
        if policy:
            return policy

        policy = cls.objects.first()
        if policy:
            if not policy.is_active:
                policy.is_active = True
                policy.save(update_fields=['is_active'])
            return policy

        return cls.objects.create(name='Default Policy', free_days=5, fine_per_day=Decimal('10.00'), max_request_days=30, is_active=True)


class BookBorrowing(models.Model):
    """Book borrowing records"""
    BORROW_STATUS = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        LibraryBook, on_delete=models.CASCADE, 
        related_name='borrowings'
    )
    student = models.ForeignKey(
        'lms_cors.Student', on_delete=models.CASCADE, 
        related_name='book_borrowings', null=True, blank=True
    )
    teacher = models.ForeignKey(
        'lms_cors.Teacher', on_delete=models.CASCADE, 
        related_name='book_borrowings', null=True, blank=True
    )
    borrowed_date = models.DateField(auto_now_add=True)
    requested_days = models.PositiveSmallIntegerField(default=5)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BORROW_STATUS, default='borrowed')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-borrowed_date']
        db_table = 'book_borrowings'
        verbose_name = 'Book Borrowing'
        verbose_name_plural = 'Book Borrowings'
    
    def __str__(self):
        borrower = self.student.full_name if self.student else (self.teacher.full_name if self.teacher else "Unknown")
        return f"{self.book.title} - {borrower}"

    def clean(self):
        if not self.student and not self.teacher:
            raise ValidationError("Either a student or a teacher must be the borrower.")
            
        if self.pk is None and self.status == 'borrowed':
             if self.book.copies_available < 1:
                 raise ValidationError(f"Book '{self.book.title}' is not available.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if not is_new:
            try:
                old = BookBorrowing.objects.get(pk=self.pk)
                if old.status == 'borrowed' and self.status == 'returned':
                    self.book.copies_available += 1
                    self.book.save()
            except BookBorrowing.DoesNotExist:
                pass

        self.clean()
        
        if is_new and self.status == 'borrowed':
             self.book.copies_available -= 1
             self.book.save()
             
        super().save(*args, **kwargs)
