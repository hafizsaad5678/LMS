from rest_framework import serializers


class QuizInitSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    num_questions = serializers.IntegerField(default=10, min_value=1, max_value=100)
    question_type = serializers.CharField(max_length=50, default='MCQ')
    difficulty = serializers.CharField(max_length=50, default='Medium')

    def validate_num_questions(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError('num_questions must be an integer between 1 and 100')
        return value


class QuizGenerateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100, required=False)
    difficulty = serializers.CharField(max_length=50)
    question_type = serializers.CharField(max_length=500)
    num_questions = serializers.IntegerField(min_value=1, max_value=100)
    total_marks = serializers.IntegerField(min_value=1)
    temperature = serializers.FloatField(min_value=0, max_value=1, default=0.7)
    include_explanation = serializers.BooleanField(default=True)

    def validate_num_questions(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError('num_questions must be an integer between 1 and 100')
        return value


class QuizSaveSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    quiz_data = serializers.JSONField()
    # Assignment fields
    assign_mode = serializers.CharField(max_length=20)  # 'all', 'department', 'students'
    target_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    deadline = serializers.DateTimeField(required=False, allow_null=True)


class QuizRegenerateQuestionSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100)
    question_type = serializers.CharField(max_length=50)
    difficulty = serializers.CharField(max_length=50, required=False, default='Medium')
    marks = serializers.IntegerField(min_value=1, default=1)
    temperature = serializers.FloatField(min_value=0, max_value=1, default=0.7)
