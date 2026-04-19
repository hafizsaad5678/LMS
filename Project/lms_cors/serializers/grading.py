"""
Serializers for Professional Grading Management System
"""
from rest_framework import serializers
from ..models.grading import (
    GradeComponent, StudentMark, MarkEditHistory,
    GradingScheme, StudentGradeSummary,
    Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer
)


class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'option_text', 'is_correct']


class QuizOptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'option_text']

class QuizQuestionSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'quiz', 'question_text', 'question_type', 'marks', 'correct_answer_text', 'explanation', 'order', 'options']

    def validate(self, attrs):
        question_type = attrs.get('question_type') or getattr(self.instance, 'question_type', 'mcq')
        question_text = (attrs.get('question_text') or '').strip()
        marks = attrs.get('marks')

        if not question_text:
            raise serializers.ValidationError({'question_text': 'This field is required.'})

        if marks is None or marks <= 0:
            raise serializers.ValidationError({'marks': 'Marks must be greater than zero.'})

        if question_type == 'mcq':
            options = self.initial_data.get('options', [])
            if not isinstance(options, list) or len(options) < 2:
                raise serializers.ValidationError({'options': 'At least two options are required for MCQ.'})

            correct_count = 0
            for opt in options:
                text = str((opt or {}).get('option_text', '')).strip()
                if not text:
                    raise serializers.ValidationError({'options': 'Option text cannot be empty.'})
                if bool((opt or {}).get('is_correct')):
                    correct_count += 1

            if correct_count != 1:
                raise serializers.ValidationError({'options': 'Exactly one correct option is required for MCQ.'})

        if question_type in {'short_answer', 'essay'}:
            correct_text = str(attrs.get('correct_answer_text', '')).strip()
            if not correct_text:
                raise serializers.ValidationError({'correct_answer_text': 'Correct answer is required for non-MCQ questions.'})

        return attrs


class QuizQuestionPublicSerializer(serializers.ModelSerializer):
    options = QuizOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'quiz', 'question_text', 'question_type', 'marks', 'order', 'options']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    question_count = serializers.SerializerMethodField()
    last_attempt = serializers.SerializerMethodField()
    attempt_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'subject', 'subject_name', 'time_limit_minutes', 
            'total_marks', 'is_published', 'created_at', 'updated_at', 
            'created_by', 'created_by_name', 'question_count', 'last_attempt',
            'attempt_stats', 'questions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'is_published']

    def get_attempt_stats(self, obj):
        """Get stats for teacher/admin to see total attempts and student performance"""
        from django.db.models import Count, Max, Avg
        stats = obj.attempts.filter(is_submitted=True).aggregate(
            total_students=Count('student', distinct=True),
            total_attempts=Count('id'),
            max_score=Max('score'),
            avg_score=Avg('score')
        )
        return {
            'total_students': stats['total_students'] or 0,
            'total_attempts': stats['total_attempts'] or 0,
            'max_score': float(stats['max_score'] or 0),
            'avg_score': round(float(stats['avg_score'] or 0), 2)
        }

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        is_create = instance is None

        title = str(attrs.get('title', getattr(instance, 'title', ''))).strip()
        if not title:
            raise serializers.ValidationError({'title': 'This field is required.'})
        attrs['title'] = title

        subject = attrs.get('subject', getattr(instance, 'subject', None))
        if subject is None:
            raise serializers.ValidationError({'subject': 'This field is required.'})

        time_limit = attrs.get('time_limit_minutes', getattr(instance, 'time_limit_minutes', None))
        if time_limit is None or time_limit <= 0:
            raise serializers.ValidationError({'time_limit_minutes': 'Time limit must be greater than zero.'})

        # On PATCH from list/edit modal, total_marks is typically not included.
        # Validate it only when explicitly provided, or during create.
        if is_create or 'total_marks' in attrs:
            total_marks = attrs.get('total_marks')
            if total_marks is None or total_marks <= 0:
                raise serializers.ValidationError({'total_marks': 'Total marks must be greater than zero.'})

        return attrs
        
    def get_question_count(self, obj):
        return obj.questions.count()

    def get_last_attempt(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        # Only relevant for students
        if not hasattr(request.user, 'student_profile'):
            return None
            
        attempt = QuizAttempt.objects.filter(
            quiz=obj, 
            student=request.user.student_profile
        ).order_by('-started_at').first()
        
        if attempt:
            return {
                'id': attempt.id,
                'score': float(attempt.score),
                'started_at': attempt.started_at,
                'end_time': attempt.end_time,
                'completed_at': attempt.completed_at,
                'is_completed': attempt.is_completed,
                'is_submitted': attempt.is_submitted,
                'status': attempt.status,
            }
        return None


class QuizPublicSerializer(serializers.ModelSerializer):
    questions = QuizQuestionPublicSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'subject', 'subject_name', 'time_limit_minutes',
            'total_marks', 'is_published', 'question_count', 'questions'
        ]

    def get_question_count(self, obj):
        return obj.questions.count()

class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = '__all__'

class QuizAttemptSerializer(serializers.ModelSerializer):
    answer_entries = QuizAnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'student', 'user', 'started_at', 'start_time', 'end_time', 'completed_at',
            'score', 'is_completed', 'is_submitted', 'status', 'answers', 'flagged_questions',
            'answer_entries', 'student_name', 'quiz_title'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'score']


class QuizAttemptStateSerializer(serializers.ModelSerializer):
    quiz = QuizPublicSerializer(read_only=True)
    time_remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'status', 'is_completed', 'is_submitted', 'start_time',
            'end_time', 'time_remaining_seconds', 'answers', 'flagged_questions', 'score'
        ]

    def get_time_remaining_seconds(self, obj):
        from django.utils import timezone
        if not obj.end_time:
            return 0
        delta = int((obj.end_time - timezone.now()).total_seconds())
        return max(0, delta)


class QuizReviewQuestionSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)
    user_answer = serializers.SerializerMethodField()
    correct_option_id = serializers.SerializerMethodField()
    correct_option_text = serializers.SerializerMethodField()
    correct_answer_text = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()

    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question_text', 'question_type', 'marks', 'explanation',
            'options', 'user_answer', 'correct_option_id',
            'correct_option_text', 'correct_answer_text', 'obtained_marks'
        ]

    def get_user_answer(self, obj):
        answers_map = self.context.get('answers_map', {})
        return answers_map.get(str(obj.id), {})

    def get_correct_option_id(self, obj):
        if obj.question_type != 'mcq':
            return None
        option = obj.options.filter(is_correct=True).values_list('id', flat=True).first()
        return str(option) if option else None

    def get_correct_option_text(self, obj):
        if obj.question_type != 'mcq':
            return None
        option = obj.options.filter(is_correct=True).first()
        return option.option_text if option else None

    def get_correct_answer_text(self, obj):
        if obj.question_type in {'short_answer', 'essay'}:
            return obj.correct_answer_text or ''
        return None

    def get_obtained_marks(self, obj):
        answer_entries_map = self.context.get('answer_entries_map', {})
        answer_entry = answer_entries_map.get(str(obj.id))
        if not answer_entry:
            return 0
        return answer_entry.marks_earned



class GradeComponentSerializer(serializers.ModelSerializer):
    """Serializer for grade components"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    students_graded = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = GradeComponent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_students_graded(self, obj):
        """Count students who have marks entered (not null)"""
        return obj.student_marks.exclude(marks_obtained__isnull=True).count()
    
    def get_total_students(self, obj):
        """Count total students enrolled in the subject"""
        from ..models.people import StudentSubject
        return StudentSubject.objects.filter(subject=obj.subject).count()


class StudentMarkSerializer(serializers.ModelSerializer):
    """Serializer for student marks"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    component_name = serializers.CharField(source='component.name', read_only=True)
    max_marks = serializers.DecimalField(
        source='component.max_marks', 
        max_digits=6, decimal_places=2, 
        read_only=True
    )
    percentage = serializers.ReadOnlyField()
    weighted_marks = serializers.ReadOnlyField()
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    
    component_type = serializers.CharField(source='component.component_type', read_only=True)
    
    # Aliases for frontend compatibility and consistency with GradeSerializer
    assignment_title = serializers.CharField(source='component.name', read_only=True)
    subject_name = serializers.CharField(source='component.subject.name', read_only=True)
    subject_code = serializers.CharField(source='component.subject.code', read_only=True)
    total_marks = serializers.DecimalField(source='component.max_marks', max_digits=6, decimal_places=2, read_only=True)
    grade_value = serializers.SerializerMethodField()

    def get_grade_value(self, obj):
        percentage = float(obj.percentage or 0)
        if percentage >= 90:
            return 'A+'
        if percentage >= 85:
            return 'A'
        if percentage >= 80:
            return 'A-'
        if percentage >= 75:
            return 'B+'
        if percentage >= 70:
            return 'B'
        if percentage >= 65:
            return 'B-'
        if percentage >= 60:
            return 'C+'
        if percentage >= 55:
            return 'C'
        if percentage >= 50:
            return 'C-'
        if percentage >= 40:
            return 'D'
        return 'F'
    
    class Meta:
        model = StudentMark
        fields = [
            'id', 'student', 'student_name', 'student_enrollment', 
            'component', 'component_name', 'component_type',
            'assignment_title', 'subject_name', 'subject_code',
            'marks_obtained', 'total_marks', 'max_marks', 
            'percentage', 'weighted_marks', 'remarks', 
            'grade_value',
            'is_absent', 'is_locked', 'graded_by', 'graded_by_name',
            'graded_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'graded_at']


class StudentMarkBulkSerializer(serializers.Serializer):
    """Serializer for bulk mark entry"""
    student_id = serializers.UUIDField()
    marks_obtained = serializers.DecimalField(
        max_digits=6, decimal_places=2, 
        allow_null=True, required=False
    )
    remarks = serializers.CharField(allow_blank=True, required=False)
    is_absent = serializers.BooleanField(default=False)
    is_locked = serializers.BooleanField(default=False)


class MarkEditHistorySerializer(serializers.ModelSerializer):
    """Serializer for mark edit history"""
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    student_name = serializers.CharField(
        source='student_mark.student.full_name', read_only=True
    )
    component_name = serializers.CharField(
        source='student_mark.component.name', read_only=True
    )
    
    class Meta:
        model = MarkEditHistory
        fields = '__all__'
        read_only_fields = ['id', 'changed_at']


class GradingSchemeSerializer(serializers.ModelSerializer):
    """Serializer for grading schemes"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = GradingScheme
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentGradeSummarySerializer(serializers.ModelSerializer):
    """Serializer for student grade summaries"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    published_by_name = serializers.CharField(source='published_by.full_name', read_only=True)
    
    class Meta:
        model = StudentGradeSummary
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']


class StudentGradeDetailSerializer(serializers.Serializer):
    """Detailed grade breakdown for a student"""
    student_id = serializers.UUIDField()
    student_name = serializers.CharField()
    student_enrollment = serializers.CharField()
    components = serializers.ListField()
    total_obtained = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_max = serializers.DecimalField(max_digits=8, decimal_places=2)
    weighted_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = serializers.CharField()
    is_passing = serializers.BooleanField()


class GradeOverviewSerializer(serializers.Serializer):
    """Overview of grading for a subject"""
    subject_id = serializers.UUIDField()
    subject_name = serializers.CharField()
    subject_code = serializers.CharField()
    total_components = serializers.IntegerField()
    total_weightage = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_students = serializers.IntegerField()
    graded_students = serializers.IntegerField()
    pending_students = serializers.IntegerField()
    class_average = serializers.DecimalField(max_digits=5, decimal_places=2)
    components = GradeComponentSerializer(many=True)
