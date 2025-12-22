from rest_framework import serializers
from .models import (
    Institution, Department, Program, AcademicSession, Semester, Subject,
    Student, Teacher, TeacherSubject, StudentSubject,
    Assignment, SubmissionHistory, Grade, Attendance,
    Admin, Event, Holiday, Exam, Timetable,
    Fee, Expense, Account, LibraryBook, BookBorrowing
)


# ==================== ACADEMIC STRUCTURE ====================

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
        # Count students across all programs in this department
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

    def create(self, validated_data):
        program = super().create(validated_data)
        # Auto-generation of semesters removed as per user request
        return program


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
    id = serializers.CharField(read_only=True)  # UUID as string
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())
    program_name = serializers.CharField(source='program.name', read_only=True, allow_blank=True)
    
    session_name = serializers.CharField(source='session.session_name', read_only=True, allow_null=True)
    subject_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Semester
        fields = ['id', 'program', 'program_name', 'session', 'session_name', 'number', 'name', 'start_date', 'end_date', 'status', 'created_at', 'updated_at', 'subject_count']
        read_only_fields = ['id', 'program_name', 'created_at', 'updated_at']

    def get_subject_count(self, obj):
        return obj.subjects.count()


class SubjectSerializer(serializers.ModelSerializer):
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    program_name = serializers.CharField(source='semester.program.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = '__all__'


# ==================== PEOPLE ====================

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
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = BaseProfileSerializer.Meta.read_only_fields + ['enrollment_number']
    
    def get_current_semester_name(self, obj):
        if obj.current_semester:
            return f"Semester {obj.current_semester}"
        return None


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


# ==================== JUNCTION TABLES ====================

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
        # Return the first assigned teacher's name, or None
        if obj.subject:
            teacher_assign = obj.subject.assigned_teachers.first()
            if teacher_assign and teacher_assign.teacher:
                return teacher_assign.teacher.full_name
        return None


# ==================== ACADEMIC MANAGEMENT ====================

class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubmissionHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = SubmissionHistory
        fields = '__all__'
        read_only_fields = ['id', 'submitted_at']


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='submission.student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='submission.assignment.title', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ['id', 'graded_at']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'marked_at']


# ==================== ADMINISTRATION ====================

class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# ==================== ACADEMIC SCHEDULING ====================

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


# ==================== MANAGEMENT/FINANCIAL ====================

class FeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    balance = serializers.ReadOnlyField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    
    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']



class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


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


# ==================== NESTED/DETAIL SERIALIZERS ====================

class InstitutionDetailSerializer(InstitutionSerializer):
    """Institution with nested departments"""
    departments = DepartmentSerializer(many=True, read_only=True)


class DepartmentDetailSerializer(DepartmentSerializer):
    """Department with nested programs and teachers"""
    institution = InstitutionSerializer(read_only=True)
    programs = ProgramSerializer(many=True, read_only=True)
    teachers = TeacherSerializer(many=True, read_only=True)


class ProgramDetailSerializer(ProgramSerializer):
    """Program with nested semesters and students"""
    department = DepartmentSerializer(read_only=True)
    semesters = SemesterSerializer(source='semesters_legacy', many=True, read_only=True)
    students = StudentSerializer(source='students_legacy', many=True, read_only=True)


class AcademicSessionDetailSerializer(AcademicSessionSerializer):
    """Academic Session with nested semesters"""
    semesters = SemesterSerializer(many=True, read_only=True)


class StudentDetailSerializer(StudentSerializer):
    """Student with enrolled subjects and submissions"""
    enrolled_subjects = StudentSubjectSerializer(many=True, read_only=True)
    submissions = SubmissionHistorySerializer(many=True, read_only=True)
    attendance_records = AttendanceSerializer(many=True, read_only=True)
    fees = FeeSerializer(many=True, read_only=True)


class TeacherDetailSerializer(TeacherSerializer):
    """Teacher with teaching subjects and created assignments"""
    teaching_subjects = TeacherSubjectSerializer(many=True, read_only=True)
    created_assignments = AssignmentSerializer(many=True, read_only=True)
    marked_attendance = AttendanceSerializer(many=True, read_only=True)