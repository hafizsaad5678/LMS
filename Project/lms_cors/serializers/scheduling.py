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

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        day = (attrs.get('day') if 'day' in attrs else getattr(instance, 'day', None))
        start_time = attrs.get('start_time') if 'start_time' in attrs else getattr(instance, 'start_time', None)
        end_time = attrs.get('end_time') if 'end_time' in attrs else getattr(instance, 'end_time', None)
        teacher = attrs.get('teacher') if 'teacher' in attrs else getattr(instance, 'teacher', None)
        room = attrs.get('room') if 'room' in attrs else getattr(instance, 'room', None)
        program = attrs.get('program') if 'program' in attrs else getattr(instance, 'program', None)
        semester = attrs.get('semester') if 'semester' in attrs else getattr(instance, 'semester', None)
        is_active = attrs.get('is_active') if 'is_active' in attrs else getattr(instance, 'is_active', True)

        if day:
            day = str(day).lower()
            attrs['day'] = day

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})

        if not (day and start_time and end_time and is_active):
            return attrs

        overlap_qs = Timetable.objects.filter(
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
            is_active=True,
        )

        if instance:
            overlap_qs = overlap_qs.exclude(pk=instance.pk)

        if teacher and overlap_qs.filter(teacher=teacher).exists():
            raise serializers.ValidationError({'teacher': f'Teacher {teacher.full_name} is already booked in this time range.'})

        if room and overlap_qs.filter(room=room).exists():
            raise serializers.ValidationError({'room': f'Room {room} is occupied in this time range.'})

        if program and semester and overlap_qs.filter(program=program, semester=semester).exists():
            raise serializers.ValidationError(
                {'non_field_errors': [f'Semester {semester.number} of {program.name} already has a class in this time range.']}
            )

        return attrs
