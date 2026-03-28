from rest_framework import serializers
from ..models import LibraryBook, BookBorrowing


class LibraryBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryBook
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookBorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    
    class Meta:
        model = BookBorrowing
        fields = '__all__'
        read_only_fields = ['id', 'borrowed_date']
