from django.contrib import admin
from ..models import LibraryBook, BookBorrowing


@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'copies_total', 'copies_available', 'status']
    list_filter = ['status', 'category', 'publication_year']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    list_editable = ['status']
    ordering = ['title']
    list_per_page = 25


@admin.register(BookBorrowing)
class BookBorrowingAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower_display', 'borrowed_date', 'due_date', 'returned_date', 'status', 'fine_amount']
    list_filter = ['status', 'borrowed_date', 'due_date']
    search_fields = ['book__title', 'student__full_name', 'teacher__full_name']
    list_editable = ['status']
    ordering = ['-borrowed_date']
    list_per_page = 20
    
    @admin.display(description='Borrower')
    def borrower_display(self, obj):
        if obj.student:
            return f"Student: {obj.student.full_name}"
        elif obj.teacher:
            return f"Teacher: {obj.teacher.full_name}"
        return "Unknown"
