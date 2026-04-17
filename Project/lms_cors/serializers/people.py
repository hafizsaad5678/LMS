from rest_framework import serializers
from ..models import Student, Teacher, Admin, TeacherSubject, StudentSubject


class BaseProfileSerializer(serializers.ModelSerializer):
    """Base serializer for profile models with common read-only fields"""
    age = serializers.ReadOnlyField()
    age_display = serializers.ReadOnlyField()
    profile_status = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    
    class Meta:
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'age', 
            'age_display', 'profile_status', 'edit_count',
            'verified_at', 'suspended_at', 'last_login_at', 'user'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'This field is required.'})

        # Avoid model auto-user creation so credentials email uses the provided password.
        model_class = self.Meta.model
        instance = model_class(**validated_data)
        instance._skip_auto_user_creation = True
        instance.save()
        instance.create_user_account(password)

        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.reset_password(password)
        return instance


class StudentSerializer(BaseProfileSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    department_name = serializers.CharField(source='program.department.name', read_only=True)
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    current_semester_name = serializers.SerializerMethodField()
    completed_assignments = serializers.SerializerMethodField()
    pending_assignments = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = BaseProfileSerializer.Meta.read_only_fields + ['enrollment_number']

    def validate(self, attrs):
        program = attrs.get('program', getattr(self.instance, 'program', None))
        session = attrs.get('session', getattr(self.instance, 'session', None))

        if self.instance is None:
            if not program:
                raise serializers.ValidationError({'program': 'Program/Course is required to create a student.'})
            if not session:
                raise serializers.ValidationError({'session': 'Academic session is required to create a student.'})

        if program and session and session.program_id and session.program_id != program.id:
            raise serializers.ValidationError({'session': 'Selected session does not belong to the selected program/course.'})

        if program and program.department and program.department.is_active is False:
            raise serializers.ValidationError({'program': 'Selected program belongs to an inactive department.'})

        if program and program.department and program.department.institution and program.department.institution.is_active is False:
            raise serializers.ValidationError({'program': 'Selected program belongs to an inactive institution.'})

        if session and getattr(session, 'is_active', True) is False:
            raise serializers.ValidationError({'session': 'Selected session is inactive.'})

        return attrs
    
    def get_current_semester_name(self, obj):
        if obj.current_semester:
            return f"Semester {obj.current_semester}"
        return None
    
    def get_completed_assignments(self, obj):
        """Count completed/submitted assignments"""
        from ..models import SubmissionHistory
        return SubmissionHistory.objects.filter(student=obj).count()
    
    def get_pending_assignments(self, obj):
        """Count pending assignments (assigned but not submitted)"""
        from ..models import Assignment, SubmissionHistory
        from django.utils import timezone
        
        # Get all subjects the student is enrolled in
        enrolled_subject_ids = obj.enrolled_subjects.values_list('subject_id', flat=True)
        
        # Get all assignments for those subjects that are still due
        total_assignments = Assignment.objects.filter(
            subject_id__in=enrolled_subject_ids,
            due_date__gte=timezone.now()
        ).count()
        
        # Get submitted assignments (only for assignments that are still due)
        submitted = SubmissionHistory.objects.filter(
            student=obj,
            assignment__due_date__gte=timezone.now()
        ).count()
        
        return max(0, total_assignments - submitted)
    
    def get_attendance_rate(self, obj):
        """Calculate attendance percentage"""
        from ..models import Attendance
        
        total_classes = Attendance.objects.filter(student=obj).count()
        if total_classes == 0:
            return 0
        
        present_classes = Attendance.objects.filter(student=obj, status='present').count()
        return round((present_classes / total_classes) * 100, 1)


class TeacherSerializer(BaseProfileSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = BaseProfileSerializer.Meta.read_only_fields + ['employee_id']

    def validate(self, attrs):
        department = attrs.get('department', getattr(self.instance, 'department', None))
        if self.instance is None and not department:
            raise serializers.ValidationError({'department': 'Department is required to create a teacher.'})
        if department and department.is_active is False:
            raise serializers.ValidationError({'department': 'Selected department is inactive.'})
        if department and department.institution and department.institution.is_active is False:
            raise serializers.ValidationError({'department': 'Selected department belongs to an inactive institution.'})
        return attrs


class AdminSerializer(BaseProfileSerializer):
    def validate(self, attrs):
        if self.instance is None and not str(attrs.get('role', '')).strip():
            raise serializers.ValidationError({'role': 'This field is required.'})
        return attrs

    class Meta:
        model = Admin
        fields = '__all__'
        read_only_fields = BaseProfileSerializer.Meta.read_only_fields + ['admin_id']


class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    semester_name = serializers.CharField(source='subject.semester.name', read_only=True)
    credit_hours = serializers.IntegerField(source='subject.credit_hours', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherSubject
        fields = '__all__'

    def validate(self, attrs):
        teacher = attrs.get('teacher')
        subject = attrs.get('subject')

        if self.instance is None:
            if not teacher:
                raise serializers.ValidationError({'teacher': 'Teacher is required for subject assignment.'})
            if not subject:
                raise serializers.ValidationError({'subject': 'Subject is required for teacher assignment.'})

        if teacher and subject and subject.semester and subject.semester.program and subject.semester.program.department and teacher.department:
            if teacher.department_id != subject.semester.program.department_id:
                raise serializers.ValidationError({'teacher': 'Teacher department must match subject program department.'})

        return attrs

    def get_student_count(self, obj):
        if obj.subject:
            return obj.subject.enrolled_students.count()
        return 0


class StudentSubjectSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    credit_hours = serializers.IntegerField(source='subject.credit_hours', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentSubject
        fields = '__all__'

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))
        subject = attrs.get('subject', getattr(self.instance, 'subject', None))
        semester = attrs.get('semester', getattr(self.instance, 'semester', None))

        if self.instance is None:
            if not student:
                raise serializers.ValidationError({'student': 'Student is required for enrollment.'})
            if not subject:
                raise serializers.ValidationError({'subject': 'Subject is required for enrollment.'})

        subject_semester = subject.semester if subject else None
        effective_semester = semester or subject_semester

        if self.instance is None and not effective_semester:
            raise serializers.ValidationError({'semester': 'Semester is required for enrollment (directly or through selected subject).'})

        if semester and subject_semester and semester.id != subject_semester.id:
            raise serializers.ValidationError({'semester': 'Selected semester does not match the subject semester.'})

        if student and subject_semester and subject_semester.program and student.program_id and student.program_id != subject_semester.program_id:
            raise serializers.ValidationError({'student': 'Student program does not match subject program.'})

        if student and student.session_id and subject_semester and subject_semester.session_id and student.session_id != subject_semester.session_id:
            raise serializers.ValidationError({'student': 'Student session does not match subject semester session.'})

        if student and student.program and student.program.department and student.program.department.is_active is False:
            raise serializers.ValidationError({'student': 'Selected student belongs to an inactive department hierarchy.'})

        if student and student.session and getattr(student.session, 'is_active', True) is False:
            raise serializers.ValidationError({'student': 'Selected student belongs to an inactive session.'})

        if subject and subject.semester and subject.semester.session and getattr(subject.semester.session, 'is_active', True) is False:
            raise serializers.ValidationError({'subject': 'Selected subject belongs to an inactive session.'})

        return attrs
        
    def get_teacher_name(self, obj):
        if obj.subject:
            teacher_assign = obj.subject.assigned_teachers.first()
            if teacher_assign and teacher_assign.teacher:
                return teacher_assign.teacher.full_name
        return None


# Detail Serializers
class StudentDetailSerializer(StudentSerializer):
    """Student with enrolled subjects and submissions"""
    from .assignments import SubmissionHistorySerializer
    from .attendance import AttendanceSerializer
    from .management import FeeSerializer
    
    enrolled_subjects = StudentSubjectSerializer(many=True, read_only=True)
    submissions = SubmissionHistorySerializer(many=True, read_only=True)
    attendance_records = AttendanceSerializer(many=True, read_only=True)
    fees = FeeSerializer(many=True, read_only=True)


class TeacherDetailSerializer(TeacherSerializer):
    """Teacher with teaching subjects and created assignments"""
    from .assignments import AssignmentSerializer
    from .attendance import AttendanceSerializer
    
    teaching_subjects = TeacherSubjectSerializer(many=True, read_only=True)
    created_assignments = AssignmentSerializer(many=True, read_only=True)
    marked_attendance = AttendanceSerializer(many=True, read_only=True)
