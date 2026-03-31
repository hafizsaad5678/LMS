import logging

from openai import APITimeoutError
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
from ai_core.services.quiz.saver import QuizSaveService
from ai_core.services.config import (
    QUIZ_DEFAULT_DIFFICULTY,
    QUIZ_DEFAULT_NUM_QUESTIONS,
    QUIZ_DEFAULT_QUESTION_TYPE,
    QUIZ_DEFAULT_TEMPERATURE,
)
from lms_cors.models.academic import Subject
from lms_cors.models.people import Teacher

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
            payload, response_code = QuizSaveService.save_quiz(serializer.validated_data, request.user)
            return Response(payload, status=response_code)

        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
        except Teacher.DoesNotExist:
            return Response({'error': 'Only teachers can save quizzes.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
