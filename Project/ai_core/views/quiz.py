import json
import logging
from datetime import timedelta

from openai import APITimeoutError
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ai_core.serializers import (
    QuizGenerateSerializer,
    QuizInitSerializer,
    QuizRegenerateQuestionSerializer,
    QuizSaveSerializer,
)
from ai_core.services.quiz.generator import QuizGeneratorService
from ai_core.services.config import (
    QUIZ_DEFAULT_DIFFICULTY,
    QUIZ_DEFAULT_NUM_QUESTIONS,
    QUIZ_DEFAULT_QUESTION_TYPE,
    QUIZ_DEFAULT_TEMPERATURE,
    QUIZ_DUPLICATE_WINDOW_SECONDS,
    QUIZ_GRADE_COMPONENT_STATUS,
    QUIZ_GRADE_COMPONENT_WEIGHTAGE,
)
from lms_cors.models.academic import Subject
from lms_cors.models.grading import GradeComponent, Quiz, QuizOption, QuizQuestion
from lms_cors.models.people import Student, StudentSubject, Teacher

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_init(request):
    """
    Step 1 & 2: Get initial suggestions or ask follow-up configuration
    """
    serializer = QuizInitSerializer(data=request.data)
    if serializer.is_valid():
        try:
            suggestions = QuizGeneratorService.get_initial_suggestions(
                serializer.validated_data['topic'],
                serializer.validated_data['subject'],
                serializer.validated_data['department'],
                num_questions=serializer.validated_data.get('num_questions', QUIZ_DEFAULT_NUM_QUESTIONS),
                question_type=serializer.validated_data.get('question_type', QUIZ_DEFAULT_QUESTION_TYPE),
                difficulty=serializer.validated_data.get('difficulty', QUIZ_DEFAULT_DIFFICULTY)
            )
            return Response(suggestions)
        except APITimeoutError:
            logger.exception('quiz_init timeout')
            return Response(
                {'error': 'AI provider timed out while preparing quiz suggestions. Please try again.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            logger.exception('quiz_init failed')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.warning('quiz_init validation errors: %s', serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_generate(request):
    """
    Step 3: Generate full quiz JSON
    """
    serializer = QuizGenerateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            config = serializer.validated_data
            quiz_data = QuizGeneratorService.generate_full_quiz(
                config['topic'],
                config['subject'],
                config,
                temperature=config.get('temperature', QUIZ_DEFAULT_TEMPERATURE)
            )
            return Response(quiz_data)
        except APITimeoutError:
            logger.exception('quiz_generate timeout')
            return Response(
                {'error': 'AI provider timed out while generating the quiz. Please retry in a moment.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            logger.exception('quiz_generate failed')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.warning('quiz_generate validation errors: %s', serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_regenerate_question(request):
    """
    Regenerate a specific single question instead of the full quiz.
    """
    serializer = QuizRegenerateQuestionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            config = serializer.validated_data
            question_data = QuizGeneratorService.generate_single_question(
                config['topic'],
                config['subject'],
                config,
                temperature=config.get('temperature', QUIZ_DEFAULT_TEMPERATURE)
            )
            return Response(question_data)
        except APITimeoutError:
            logger.exception('quiz_regenerate_question timeout')
            return Response(
                {'error': 'AI provider timed out while regenerating the question. Please retry.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_save(request):
    """
    Step 6: Save quiz and handle assignments
    """
    serializer = QuizSaveSerializer(data=request.data)
    if serializer.is_valid():
        try:
            data = serializer.validated_data

            # Duplicate protection: check if same quiz created in last 10 seconds.
            recent_time = timezone.now() - timedelta(seconds=QUIZ_DUPLICATE_WINDOW_SECONDS)
            existing_quiz = Quiz.objects.filter(
                title=data['title'],
                subject_id=data['subject_id'],
                created_by__user=request.user,
                created_at__gte=recent_time
            ).first()

            if existing_quiz:
                return Response({
                    'message': 'Duplicate quiz submission detected. Returning existing record.',
                    'quiz_id': str(existing_quiz.id),
                    'already_exists': True
                }, status=status.HTTP_200_OK)

            subject = Subject.objects.get(id=data['subject_id'])

            try:
                teacher = Teacher.objects.get(user=request.user)
            except Teacher.DoesNotExist:
                return Response({'error': 'Only teachers can save quizzes.'}, status=status.HTTP_403_FORBIDDEN)

            quiz_json = data['quiz_data']

            # 1. Create grade component.
            grade_comp = GradeComponent.objects.create(
                subject=subject,
                created_by=teacher,
                name=data['title'],
                component_type='quiz',
                max_marks=quiz_json.get('total_marks', 0),
                weightage=QUIZ_GRADE_COMPONENT_WEIGHTAGE,
                status=QUIZ_GRADE_COMPONENT_STATUS,
            )

            # 2. Create quiz.
            quiz = Quiz.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                subject=subject,
                created_by=teacher,
                grade_component=grade_comp,
                is_published=True
            )

            # 3. Create questions and options.
            for q_data in quiz_json.get('questions', []):
                q_type_map = {
                    'MCQ': 'mcq',
                    'Short Answer': 'short_answer',
                    'Long Answer': 'essay',
                    'Mixed': 'mcq'
                }

                question = QuizQuestion.objects.create(
                    quiz=quiz,
                    question_text=q_data['question_text'],
                    question_type=q_type_map.get(q_data.get('question_type', 'MCQ'), 'mcq'),
                    marks=q_data.get('marks', 1),
                    correct_answer_text=q_data.get('correct_answer_text', q_data.get('correct_answer', '')),
                    explanation=q_data.get('explanation', '')
                )

                if q_data.get('question_type', 'MCQ') == 'MCQ':
                    for opt_data in q_data.get('options', []):
                        if isinstance(opt_data, dict):
                            text = opt_data.get('text', '')
                            is_correct = opt_data.get('is_correct', False)
                        else:
                            text = opt_data
                            is_correct = (text == q_data.get('correct_answer'))

                        QuizOption.objects.create(
                            question=question,
                            option_text=text,
                            is_correct=is_correct
                        )

            # 4. Handle assignments (QuizAttempts / StudentMarks).
            assign_mode = data.get('assign_mode', 'all')
            target_ids = data.get('target_ids', [])

            assigned_students = []
            if assign_mode == 'all':
                student_subjects = StudentSubject.objects.filter(subject=subject)
                assigned_students = [ss.student for ss in student_subjects]
            elif assign_mode == 'department':
                student_subjects = StudentSubject.objects.filter(subject=subject).select_related('student', 'student__program')
                assigned_students = [
                    ss.student for ss in student_subjects
                    if ss.student.program and ss.student.program.department_id and ss.student.program.department_id in target_ids
                ]
            elif assign_mode == 'students':
                assigned_students = list(Student.objects.filter(id__in=target_ids))

            assignment_metadata = {
                'assign_mode': assign_mode,
                'target_ids': target_ids,
                'deadline': data.get('deadline')
            }
            quiz.description = json.dumps(assignment_metadata, cls=DjangoJSONEncoder)
            quiz.save()

            from lms_cors.models.grading import QuizAttempt, StudentMark
            for student in assigned_students:
                QuizAttempt.objects.get_or_create(quiz=quiz, student=student)
                StudentMark.objects.get_or_create(component=grade_comp, student=student)

            return Response({
                'message': 'Quiz generated and assigned successfully',
                'quiz_id': str(quiz.id),
                'assigned_count': len(assigned_students)
            }, status=status.HTTP_201_CREATED)

        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
