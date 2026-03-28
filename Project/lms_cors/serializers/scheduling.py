from rest_framework import serializers
from ..models import Event, Holiday, Exam, Timetable


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class HolidaySerializer(serializers.ModelSerializer):
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    program_name = serializers.CharField(source='subject.semester.program.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    
    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
