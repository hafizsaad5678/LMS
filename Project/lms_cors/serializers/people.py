from rest_framework import serializers
from ..models import Student, Teacher, Admin, TeacherSubject, StudentSubject


class BaseProfileSerializer(serializers.ModelSerializer):
    """Base serializer for profile models with common read-only fields"""
    age = serializers.ReadOnlyField()
    age_display = serializers.ReadOnlyField()
    profile_status = serializers.ReadOnlyField()
    
    class Meta:
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'age', 
            'age_display', 'profile_status', 'edit_count',
            'verified_at', 'suspended_at', 'last_login_at', 'user'
        ]


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


class AdminSerializer(BaseProfileSerializer):
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
