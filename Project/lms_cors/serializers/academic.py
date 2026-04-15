from rest_framework import serializers
from ..models import (
    Institution, Department, Program, AcademicSession, Semester, Subject,
    Student, Teacher, TeacherSubject, Timetable, Grade, StudentMark
)


class InstitutionSerializer(serializers.ModelSerializer):
    """Serializer for Institution model"""
    department_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Institution
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_department_count(self, obj):
        return obj.departments.count()


class DepartmentSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    institution_code = serializers.CharField(source='institution.code', read_only=True)
    program_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_program_count(self, obj):
        return obj.programs.count()
    
    def get_teacher_count(self, obj):
        return obj.teachers.count()
    
    def get_student_count(self, obj):
        return Student.objects.filter(program__department=obj).count()


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    semester_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = '__all__'
    
    def get_semester_count(self, obj):
        return obj.semesters_legacy.count()
    
    def get_student_count(self, obj):
        return obj.students_legacy.count()


class AcademicSessionSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    department_name = serializers.CharField(source='program.department.name', read_only=True)
    program_level = serializers.CharField(source='program.program_level', read_only=True)
    program_level_display = serializers.SerializerMethodField()
    semester_count = serializers.SerializerMethodField()
    current_enrollment = serializers.SerializerMethodField()
    capacity_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicSession
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'edit_count']
    
    def get_program_level_display(self, obj):
        if obj.program and obj.program.program_level:
            return obj.program.get_program_level_display()
        return None
    
    def get_semester_count(self, obj):
        return obj.semesters.count()
    
    def get_current_enrollment(self, obj):
        return obj.students.count()
    
    def get_capacity_percentage(self, obj):
        total_capacity = getattr(obj, 'total_capacity', None)
        if total_capacity and total_capacity > 0:
            return (obj.students.count() / total_capacity) * 100
        return 0


class SemesterSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())
    program_name = serializers.CharField(source='program.name', read_only=True, allow_blank=True)
    session_name = serializers.CharField(source='session.session_name', read_only=True, allow_null=True)
    subject_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Semester
        fields = ['id', 'program', 'program_name', 'session', 'session_name', 'number', 'name', 
                  'start_date', 'end_date', 'status', 'created_at', 'updated_at', 'subject_count']
        read_only_fields = ['id', 'program_name', 'created_at', 'updated_at']

    def get_subject_count(self, obj):
        return obj.subjects.count()


class SubjectSerializer(serializers.ModelSerializer):
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    program_name = serializers.CharField(source='semester.program.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = '__all__'


class SubjectDetailSerializer(SubjectSerializer):
    department_name = serializers.CharField(source='semester.program.department.name', read_only=True)
    teacher = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    
    def get_teacher(self, obj):
        assignment = obj.assigned_teachers.filter(is_active=True).first()
        if assignment and assignment.teacher:
            # Return basic teacher info object or just ID
            return {
                'id': str(assignment.teacher.id),
                'email': assignment.teacher.email,
                'user': {
                    'first_name': assignment.teacher.user.first_name,
                    'last_name': assignment.teacher.user.last_name
                }
            }
        return None
        
    def get_teacher_name(self, obj):
        assignment = obj.assigned_teachers.filter(is_active=True).first()
        if assignment and assignment.teacher:
            return assignment.teacher.full_name
        return None
        
    def get_schedule(self, obj):
        slots = Timetable.objects.filter(subject=obj, is_active=True)
        return [
            {
                'day': slot.day,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'room': slot.room
            }
            for slot in slots
        ]

    attendance_summary = serializers.SerializerMethodField()
    current_grade = serializers.SerializerMethodField()

    def get_attendance_summary(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            from ..models import Attendance
            records = Attendance.objects.filter(subject=obj, student=student)
            total = records.count()
            if total > 0:
                present = records.filter(status='present').count()
                return round((present / total) * 100, 1)
        return None

    def get_current_grade(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'student_profile'):
            return None

        student = request.user.student_profile

        total_obtained = 0.0
        total_possible = 0.0

        # Assignment grades (linked via submission history)
        assignment_grades = Grade.objects.filter(
            submission__student=student,
            submission__assignment__subject=obj,
        ).select_related('submission__assignment')

        for grade in assignment_grades:
            obtained = float(grade.marks_obtained or 0)
            possible = float((grade.submission.assignment.total_marks if grade.submission and grade.submission.assignment else 0) or 0)
            if possible > 0:
                total_obtained += obtained
                total_possible += possible

        # Other assessment components (quiz, midterm, final, etc.)
        component_marks = StudentMark.objects.filter(
            student=student,
            component__subject=obj,
            marks_obtained__isnull=False,
        ).select_related('component')

        for mark in component_marks:
            obtained = float(mark.marks_obtained or 0)
            possible = float((mark.component.max_marks if mark.component else 0) or 0)
            if possible > 0:
                total_obtained += obtained
                total_possible += possible

        if total_possible <= 0:
            return "N/A"

        percentage = round((total_obtained / total_possible) * 100, 1)

        if percentage >= 90:
            letter = 'A+'
        elif percentage >= 85:
            letter = 'A'
        elif percentage >= 80:
            letter = 'A-'
        elif percentage >= 75:
            letter = 'B+'
        elif percentage >= 70:
            letter = 'B'
        elif percentage >= 65:
            letter = 'B-'
        elif percentage >= 60:
            letter = 'C+'
        elif percentage >= 55:
            letter = 'C'
        elif percentage >= 50:
            letter = 'C-'
        elif percentage >= 40:
            letter = 'D'
        else:
            letter = 'F'

        return f"{letter} ({percentage}%)"


# Detail Serializers (with nested data)
class InstitutionDetailSerializer(InstitutionSerializer):
    """Institution with nested departments"""
    departments = DepartmentSerializer(many=True, read_only=True)


class DepartmentDetailSerializer(DepartmentSerializer):
    """Department with nested programs and teachers"""
    institution = InstitutionSerializer(read_only=True)
    programs = ProgramSerializer(many=True, read_only=True)


class ProgramDetailSerializer(ProgramSerializer):
    """Program with nested semesters and students"""
    department = DepartmentSerializer(read_only=True)
    semesters = SemesterSerializer(source='semesters_legacy', many=True, read_only=True)


class AcademicSessionDetailSerializer(AcademicSessionSerializer):
    """Academic Session with nested semesters"""
    semesters = SemesterSerializer(many=True, read_only=True)
