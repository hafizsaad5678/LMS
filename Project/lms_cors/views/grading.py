from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from ..models.grading import GradeComponent, StudentMark, Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer
from ..models.people import Student, StudentSubject
from ..serializers.grading import (
    GradeComponentSerializer, 
    StudentMarkSerializer,
    StudentMarkBulkSerializer,
    QuizSerializer,
    QuizPublicSerializer,
    QuizQuestionSerializer,
    QuizOptionSerializer,
    QuizAttemptSerializer,
    QuizAttemptStateSerializer,
    QuizReviewQuestionSerializer,
    QuizAnswerSerializer
)


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' and hasattr(self.request.user, 'student_profile'):
            return QuizPublicSerializer
        return QuizSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Quiz.objects.none()

        queryset = Quiz.objects.all()
        
        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            # Admins see everything
            pass
        elif hasattr(user, 'teacher_profile'):
            # Teachers see what they created
            queryset = queryset.filter(created_by=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            # Students see published quizzes for their enrolled subjects
            student = user.student_profile
            enrolled_subject_ids = StudentSubject.objects.filter(
                student=student
            ).values_list('subject_id', flat=True)
            
            queryset = queryset.filter(
                is_published=True,
                subject_id__in=enrolled_subject_ids
            )
        else:
            # Users with no recognized profile see nothing
            return Quiz.objects.none()
            
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
            
        return queryset.distinct().order_by('-created_at', 'id')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.teacher_profile)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        quiz = self.get_object()
        quiz.is_published = True
        quiz.save()
        return Response({'status': 'quiz published'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        quiz = self.get_object()
        user = request.user
        
        if not hasattr(user, 'student_profile'):
            return Response({'error': 'Only students can take quizzes'}, status=403)
            
        student = user.student_profile
        
        with transaction.atomic():
            attempt, created = QuizAttempt.objects.get_or_create(
                quiz=quiz,
                student=student,
                defaults={
                    'user': user,
                    'status': 'in_progress',
                    'is_completed': False,
                    'is_submitted': False,
                    'start_time': timezone.now(),
                    'end_time': timezone.now() + timedelta(minutes=quiz.time_limit_minutes or 30)
                }
            )

            if attempt.is_locked:
                return Response(QuizAttemptStateSerializer(attempt, context={'request': request}).data)

            if not attempt.answers:
                attempt.answers = {
                    str(q.id): {
                        'question_id': str(q.id),
                        'selected_option': None,
                        'answer_text': '',
                        'is_flagged': False,
                        'status': 'not_visited',
                        'updated_at': timezone.now().isoformat()
                    }
                    for q in quiz.questions.all()
                }
                attempt.flagged_questions = []
                attempt.save(update_fields=['answers', 'flagged_questions'])

        return Response(QuizAttemptStateSerializer(attempt, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def get_status(self, request, pk=None):
        quiz = self.get_object()
        user = request.user
        
        if not hasattr(user, 'student_profile'):
            return Response({'current_attempt': None})
            
        student = user.student_profile
        attempt = QuizAttempt.objects.filter(quiz=quiz, student=student).first()
        
        return Response({
            'current_attempt': QuizAttemptSerializer(attempt).data if attempt else None
        })

class QuizQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = QuizQuestion.objects.all()

    def perform_create(self, serializer):
        # Quiz is now in serializer fields, so it will be in validated_data
        question = serializer.save()
        self._handle_options(question)

    def perform_update(self, serializer):
        question = serializer.save()
        self._handle_options(question)

    def _handle_options(self, question):
        if question.question_type == 'mcq':
            # Get options from raw request data as they are read-only in serializer
            options_data = self.request.data.get('options', [])
            if options_data:
                # Clear existing options for this question
                QuizOption.objects.filter(question=question).delete()
                # Create new options
                for opt_data in options_data:
                    # Remove id if it exists in opt_data to avoid conflicts with UUID primary key
                    opt_data_clean = {k: v for k, v in opt_data.items() if k != 'id'}
                    QuizOption.objects.create(question=question, **opt_data_clean)

class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return QuizAttempt.objects.none()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            return QuizAttempt.objects.all()
            
        if hasattr(user, 'teacher_profile'):
            # Teachers see attempts for their quizzes
            return QuizAttempt.objects.filter(quiz__created_by=user.teacher_profile)

        if hasattr(user, 'student_profile'):
            return QuizAttempt.objects.filter(student=user.student_profile)

        return QuizAttempt.objects.none()

    def create(self, request, *args, **kwargs):
        return Response(
            {'error': 'Create attempts via /quizzes/{id}/start/ endpoint only.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def _evaluate_attempt(self, attempt):
        answers_map = attempt.answers or {}
        total_score = Decimal('0')
        flagged = []

        for question in attempt.quiz.questions.all():
            payload = answers_map.get(str(question.id), {})
            selected_option_id = payload.get('selected_option')
            answer_text = payload.get('answer_text') or ''
            is_flagged = bool(payload.get('is_flagged'))
            status_value = payload.get('status') or 'not_visited'

            marks_earned = Decimal('0')

            if question.question_type == 'mcq' and selected_option_id:
                selected_option = QuizOption.objects.filter(id=selected_option_id, question=question).first()
                if selected_option and selected_option.is_correct:
                    marks_earned = Decimal(str(question.marks))
            elif question.question_type == 'short_answer' and answer_text:
                correct_text = (question.correct_answer_text or '').strip().lower()
                student_text = str(answer_text).strip().lower()
                if correct_text and student_text == correct_text:
                    marks_earned = Decimal(str(question.marks))

            if is_flagged:
                flagged.append(str(question.id))

            total_score += marks_earned

            QuizAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_option_id': selected_option_id if selected_option_id else None,
                    'answer_text': answer_text,
                    'marks_earned': marks_earned,
                    'status': status_value,
                    'is_flagged': is_flagged
                }
            )

        attempt.flagged_questions = flagged
        attempt.score = total_score

    def _close_attempt(self, attempt, close_status):
        attempt.is_completed = True
        attempt.is_submitted = True
        attempt.status = close_status
        attempt.completed_at = timezone.now()
        self._evaluate_attempt(attempt)
        attempt.status = 'evaluated'
        attempt.save()

    def _handle_expired_attempt(self, attempt):
        if not attempt.is_locked and attempt.is_expired:
            self._close_attempt(attempt, 'auto_submitted')
            attempt.refresh_from_db()

    def _can_force_end(self, user):
        return bool(user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'))

    @action(detail=True, methods=['get'])
    def state(self, request, pk=None):
        attempt = self.get_object()
        self._handle_expired_attempt(attempt)
        serializer = QuizAttemptStateSerializer(attempt, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def autosave(self, request, pk=None):
        attempt = self.get_object()

        if attempt.is_locked:
            return Response({'error': 'Attempt is already closed.'}, status=status.HTTP_400_BAD_REQUEST)

        if attempt.is_expired:
            self._close_attempt(attempt, 'auto_submitted')
            return Response({'error': 'Time is over. Attempt auto-submitted.'}, status=status.HTTP_409_CONFLICT)

        question_id = str(request.data.get('question_id') or '')
        if not question_id:
            raise ValidationError('question_id is required.')

        question = QuizQuestion.objects.filter(id=question_id, quiz=attempt.quiz).first()
        if not question:
            raise ValidationError('Invalid question_id for this attempt.')

        answers_map = attempt.answers or {}
        current = answers_map.get(question_id, {
            'question_id': question_id,
            'selected_option': None,
            'answer_text': '',
            'is_flagged': False,
            'status': 'not_visited'
        })

        selected_option = request.data.get('selected_option')
        answer_text = request.data.get('answer_text')
        is_flagged = request.data.get('is_flagged')
        status_value = request.data.get('status')

        if selected_option is not None:
            current['selected_option'] = selected_option
        if answer_text is not None:
            current['answer_text'] = answer_text
        if is_flagged is not None:
            current['is_flagged'] = bool(is_flagged)
        if status_value in {'not_visited', 'visited', 'answered'}:
            current['status'] = status_value

        if current.get('selected_option') or (current.get('answer_text') or '').strip():
            current['status'] = 'answered'

        current['updated_at'] = timezone.now().isoformat()
        answers_map[question_id] = current

        flagged = [qid for qid, item in answers_map.items() if item.get('is_flagged')]

        attempt.answers = answers_map
        attempt.flagged_questions = flagged
        attempt.save(update_fields=['answers', 'flagged_questions'])

        QuizAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_option_id': current.get('selected_option') or None,
                'answer_text': current.get('answer_text') or '',
                'status': current.get('status') or 'visited',
                'is_flagged': bool(current.get('is_flagged'))
            }
        )

        return Response({'saved': True, 'question_id': question_id, 'status': current['status']})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        attempt = self.get_object()
        answers_map = attempt.answers or {}
        total = attempt.quiz.questions.count()
        answered = 0
        visited = 0
        flagged = 0

        for item in answers_map.values():
            status_value = item.get('status')
            if status_value == 'answered':
                answered += 1
            elif status_value == 'visited':
                visited += 1
            if item.get('is_flagged'):
                flagged += 1

        return Response({
            'total_questions': total,
            'answered': answered,
            'not_answered': max(total - answered, 0),
            'visited': visited,
            'flagged': flagged,
            'status': attempt.status,
            'is_completed': attempt.is_completed
        })

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        attempt = self.get_object()

        if attempt.is_locked:
            return Response(QuizAttemptSerializer(attempt, context={'request': request}).data)

        if attempt.is_expired:
            self._close_attempt(attempt, 'auto_submitted')
        else:
            self._close_attempt(attempt, 'submitted')

        attempt.refresh_from_db()
        return Response(QuizAttemptSerializer(attempt, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def force_end(self, request, pk=None):
        attempt = self.get_object()

        if not self._can_force_end(request.user):
            return Response({'error': 'Only admin can force end attempts.'}, status=status.HTTP_403_FORBIDDEN)

        if not attempt.is_locked:
            self._close_attempt(attempt, 'force_ended')
            attempt.refresh_from_db()

        return Response(QuizAttemptSerializer(attempt, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def review(self, request, pk=None):
        attempt = self.get_object()

        if not attempt.is_locked:
            return Response({'error': 'Attempt is not submitted yet.'}, status=status.HTTP_400_BAD_REQUEST)

        questions = attempt.quiz.questions.prefetch_related('options').all()
        answer_entries_map = {
            str(entry.question_id): entry
            for entry in attempt.answer_entries.select_related('selected_option').all()
        }
        serializer = QuizReviewQuestionSerializer(
            questions,
            many=True,
            context={
                'request': request,
                'answers_map': attempt.answers or {},
                'answer_entries_map': answer_entries_map,
            }
        )

        return Response({
            'attempt_id': str(attempt.id),
            'quiz_id': str(attempt.quiz_id),
            'quiz_title': attempt.quiz.title,
            'score': attempt.score,
            'total_marks': attempt.quiz.total_marks,
            'status': attempt.status,
            'questions': serializer.data
        })


class GradeComponentViewSet(viewsets.ModelViewSet):
    serializer_class = GradeComponentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return GradeComponent.objects.none()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            queryset = GradeComponent.objects.all()
        elif hasattr(user, 'teacher_profile'):
            queryset = GradeComponent.objects.filter(created_by=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            # Students can see published grade components for their enrolled subjects
            student = user.student_profile
            enrolled_subjects = StudentSubject.objects.filter(student=student).values_list('subject_id', flat=True)
            queryset = GradeComponent.objects.filter(subject_id__in=enrolled_subjects, is_visible_to_students=True)
        else:
            return GradeComponent.objects.none()
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
            
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.teacher_profile)

    @action(detail=True, methods=['get'])
    def marks(self, request, pk=None):
        """Get all marks for this component"""
        component = self.get_object()
        marks = StudentMark.objects.filter(component=component)
        serializer = StudentMarkSerializer(marks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def bulk_marks(self, request, pk=None):
        """Bulk update marks for this component"""
        component = self.get_object()
        serializer = StudentMarkBulkSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        updated_marks = []
        for item in serializer.validated_data:
            student_id = item['student_id']
            marks_defaults = {
                'marks_obtained': item.get('marks_obtained'),
                'remarks': item.get('remarks', ''),
                'is_absent': item.get('is_absent', False),
                'is_locked': item.get('is_locked', False),
                'graded_by': request.user.teacher_profile
            }
            
            mark, created = StudentMark.objects.update_or_create(
                component=component,
                student_id=student_id,
                defaults=marks_defaults
            )
            updated_marks.append(mark)

        return Response({'status': 'success', 'updated': len(updated_marks)})

    @action(detail=True, methods=['post'])
    def initialize_students(self, request, pk=None):
        """
        Create empty mark entries for all students in the subject 
        who don't have a mark entry yet.
        """
        component = self.get_object()
        subject = component.subject
        
        # Find students enrolled in this subject
        enrollments = StudentSubject.objects.filter(subject=subject)
        student_ids = enrollments.values_list('student_id', flat=True)
        
        created_count = 0
        for student_id in student_ids:
            obj, created = StudentMark.objects.get_or_create(
                component=component,
                student_id=student_id
            )
        return Response({
            'status': 'success', 
            'message': f'Initialized {created_count} new student records',
            'total_students': len(student_ids)
        })

class StudentMarkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentMarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return StudentMark.objects.none()

        queryset = StudentMark.objects.all()
        
        # Authorization filtering
        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            # Admins see everything
            pass
        elif hasattr(user, 'teacher_profile'):
            # Teachers only see marks for their components
            queryset = queryset.filter(component__created_by=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            # Students only see their own marks
            queryset = queryset.filter(student=user.student_profile)
        else:
            return StudentMark.objects.none()

        # Input filtering
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(component__subject_id=subject_id)
            
        period = self.request.query_params.get('period')
        if period:
            if period == 'midterm':
                queryset = queryset.filter(component__component_type='midterm')
            elif period == 'final':
                queryset = queryset.filter(component__component_type='final')
            
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
            
        return queryset.distinct()
