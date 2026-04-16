from rest_framework import serializers
from ..models import Assignment, SubmissionHistory, Grade


ALLOWED_SUBMISSION_EXTENSIONS = {'.pdf', '.doc', '.docx', '.zip', '.rar'}
MAX_SUBMISSION_FILE_SIZE = 10 * 1024 * 1024


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        title = (attrs.get('title') or '').strip()
        description = (attrs.get('description') or '').strip()

        if not title:
            raise serializers.ValidationError({'title': 'This field is required.'})
        if not description:
            raise serializers.ValidationError({'description': 'This field is required.'})
        if attrs.get('due_date') is None:
            raise serializers.ValidationError({'due_date': 'This field is required.'})

        return attrs

    def get_submission_count(self, obj):
        return obj.submissions.all().count()

    def get_total_students(self, obj):
        if not obj.subject:
            return 0
        from ..models import StudentSubject
        return StudentSubject.objects.filter(subject=obj.subject).count()


class StudentAssignmentSerializer(AssignmentSerializer):
    submitted_at = serializers.SerializerMethodField()
    is_submitted = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    
    def get_submitted_at(self, obj):
        student = self.context.get('student')
        if not student: return None
        submission = obj.submissions.filter(student=student).first()
        return submission.submitted_at if submission else None
        
    def get_is_submitted(self, obj):
        student = self.context.get('student')
        if not student: return False
        return obj.submissions.filter(student=student).exists()
        
    def get_grade(self, obj):
        student = self.context.get('student')
        if not student: return None
        submission = obj.submissions.filter(student=student).first()
        if submission and hasattr(submission, 'grade') and submission.grade:
            return {
                'marks': submission.grade.marks_obtained,
                'grade': submission.grade.grade_value
            }
        return None


class SubmissionHistorySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    subject_name = serializers.CharField(source='assignment.subject.name', read_only=True, allow_null=True)
    grade = serializers.SerializerMethodField()
    submission_file = serializers.SerializerMethodField()
    file_upload_url = serializers.SerializerMethodField()
    file_url = serializers.URLField(required=False, allow_blank=True)
    comments = serializers.CharField(source='submission_text', read_only=True, allow_blank=True)
    
    class Meta:
        model = SubmissionHistory
        fields = '__all__'
        read_only_fields = ['id', 'submitted_at', 'student']

    def validate(self, attrs):
        if self.instance is None:
            assignment = attrs.get('assignment')
            file_upload = attrs.get('file_upload')

            if assignment is None:
                raise serializers.ValidationError({'assignment': 'This field is required.'})

            if file_upload is None:
                raise serializers.ValidationError({'file_upload': 'A submission file is required.'})

            filename = (getattr(file_upload, 'name', '') or '').lower()
            if not any(filename.endswith(ext) for ext in ALLOWED_SUBMISSION_EXTENSIONS):
                raise serializers.ValidationError({'file_upload': 'Unsupported file type.'})

            if getattr(file_upload, 'size', 0) > MAX_SUBMISSION_FILE_SIZE:
                raise serializers.ValidationError({'file_upload': 'File size exceeds 10MB limit.'})

        return attrs
    
    def get_grade(self, obj):
        try:
            if hasattr(obj, 'grade'):
                grade = obj.grade
                if grade:
                    return {
                        'id': str(grade.id),
                        'marks_obtained': float(grade.marks_obtained),
                        'grade_value': grade.grade_value,
                        'feedback': grade.feedback,
                        'graded_at': grade.graded_at
                    }
        except Grade.DoesNotExist:
            pass
        except Exception:
            pass
        return None
    
    def get_submission_file(self, obj):
        if obj.file_upload:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file_upload.url)
            return obj.file_upload.url
        return obj.file_url or None
    
    def get_file_upload_url(self, obj):
        if obj.file_upload:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file_upload.url)
            return obj.file_upload.url
        return None


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='submission.student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='submission.assignment.title', read_only=True)
    subject_name = serializers.CharField(source='submission.assignment.subject.name', read_only=True)
    subject_code = serializers.CharField(source='submission.assignment.subject.code', read_only=True)
    total_marks = serializers.DecimalField(source='submission.assignment.total_marks', max_digits=6, decimal_places=2, read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    percentage = serializers.SerializerMethodField()

    def get_percentage(self, obj):
        total = float((obj.submission.assignment.total_marks if obj.submission and obj.submission.assignment else 0) or 0)
        obtained = float(obj.marks_obtained or 0)
        if total <= 0:
            return 0
        return round((obtained / total) * 100, 2)
    
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ['id', 'graded_at']
