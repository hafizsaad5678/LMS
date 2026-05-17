import logging
from django.db.models import OuterRef, Subquery, Q

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
from ..models.people import Student, StudentSubject, TeacherSubject
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
from ..models.assignments import Assignment, SubmissionHistory, Grade
from ..serializers.assignments import GradeSerializer
from ..permissions import IsAdminOrTeacher, IsTeacherOrAdminForWrite


def _evaluate_attempt(attempt):
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


def _close_attempt(attempt, close_status):
    attempt.is_completed = True
    attempt.is_submitted = True
    attempt.status = close_status
    attempt.completed_at = timezone.now()
    _evaluate_attempt(attempt)
    attempt.status = 'evaluated'
    attempt.save()

    # --- AUTO-SYNC TO GRADE COMPONENTS ---
    try:
        # Check if there is an active GradeComponent linked to this Quiz
        # We match by name and subject, or we can add a formal link later.
        component = GradeComponent.objects.filter(
            name=attempt.quiz.title,
            subject=attempt.quiz.subject,
            component_type='quiz'
        ).first()

        if component:
            StudentMark.objects.update_or_create(
                component=component,
                student=attempt.student,
                defaults={
                    'marks_obtained': attempt.score,
                    'remarks': f"Auto-graded from Quiz: {attempt.quiz.title}",
                    'graded_by': attempt.quiz.created_by,
                    'is_locked': True
                }
            )
    except Exception as e:
        logging.getLogger(__name__).error("Error auto-syncing quiz grade: %s", e)
    # --------------------------------------


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy', 'publish', 'unpublish'}:
            permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

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
            # Students see published quizzes for their enrolled subjects of current semester
            student = user.student_profile
            enrolled_subject_ids = StudentSubject.objects.filter(
                student=student,
                subject__semester__number=student.current_semester
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
        if not hasattr(self.request.user, 'teacher_profile'):
            raise ValidationError('Only teachers can create quizzes.')
        serializer.save(created_by=self.request.user.teacher_profile)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        quiz = self.get_object()
        quiz.is_published = True
        quiz.save()
        return Response({'status': 'quiz published'})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        quiz = self.get_object()
        quiz.is_published = False
        quiz.save()
        return Response({'status': 'quiz unpublished'})

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

            # If an attempt was pre-created but never started, reset timing so the quiz starts fresh.
            if not created and not attempt.answers:
                attempt.answer_entries.all().delete()
                attempt.answers = {}
                attempt.flagged_questions = []
                attempt.status = 'in_progress'
                attempt.is_completed = False
                attempt.is_submitted = False
                attempt.score = 0
                attempt.completed_at = None
                attempt.start_time = timezone.now()
                attempt.end_time = timezone.now() + timedelta(minutes=quiz.time_limit_minutes or 30)
                attempt.save(update_fields=[
                    'answers', 'flagged_questions', 'status', 'is_completed', 'is_submitted',
                    'score', 'completed_at', 'start_time', 'end_time'
                ])

            # If an old in-progress attempt already expired, close it on the server
            # before returning state so the client doesn't auto-submit on first tick.
            if not created and not attempt.is_locked and attempt.is_expired:
                _close_attempt(attempt, 'auto_submitted')
                attempt.refresh_from_db()

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
    permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]
    queryset = QuizQuestion.objects.all()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return QuizQuestion.objects.none()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            return QuizQuestion.objects.all()

        if hasattr(user, 'teacher_profile'):
            return QuizQuestion.objects.filter(quiz__created_by=user.teacher_profile)

        return QuizQuestion.objects.none()

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'teacher_profile'):
            raise ValidationError('Only teachers can create quiz questions.')

        quiz = serializer.validated_data.get('quiz')
        if quiz is None:
            raise ValidationError({'quiz': 'Quiz is required.'})

        if quiz.created_by_id != self.request.user.teacher_profile.id:
            raise ValidationError({'quiz': 'You can only modify questions for your own quizzes.'})

        question = serializer.save()
        self._handle_options(question)

    def perform_update(self, serializer):
        if not hasattr(self.request.user, 'teacher_profile'):
            raise ValidationError('Only teachers can update quiz questions.')

        quiz = serializer.validated_data.get('quiz', serializer.instance.quiz)
        if quiz.created_by_id != self.request.user.teacher_profile.id:
            raise ValidationError({'quiz': 'You can only modify questions for your own quizzes.'})

        question = serializer.save()
        self._handle_options(question)

    def _handle_options(self, question):
        if question.question_type == 'mcq':
            # Get options from raw request data as they are read-only in serializer
            options_data = self.request.data.get('options', [])
            if not isinstance(options_data, list) or len(options_data) < 2:
                raise ValidationError({'options': 'At least two options are required for MCQ.'})

            normalized_options = []
            correct_count = 0
            for opt_data in options_data:
                text = str((opt_data or {}).get('option_text', '')).strip()
                if not text:
                    raise ValidationError({'options': 'Option text cannot be empty.'})

                is_correct = bool((opt_data or {}).get('is_correct'))
                correct_count += 1 if is_correct else 0
                normalized_options.append({'option_text': text, 'is_correct': is_correct})

            if correct_count != 1:
                raise ValidationError({'options': 'Exactly one correct option is required.'})

            # Clear existing options for this question
            QuizOption.objects.filter(question=question).delete()
            for opt in normalized_options:
                QuizOption.objects.create(question=question, **opt)

class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return QuizAttempt.objects.none()

        queryset = QuizAttempt.objects.all()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            # Admin returns full queryset
            pass
        elif hasattr(user, 'teacher_profile'):
            # Teachers see attempts for their quizzes
            queryset = queryset.filter(quiz__created_by=user.teacher_profile)
        elif hasattr(user, 'student_profile'):
            # Students only see their own attempts from current semester
            student = user.student_profile
            queryset = queryset.filter(
                student=student,
                quiz__subject__semester__number=student.current_semester
            )
        else:
            return QuizAttempt.objects.none()

        # Filter by quiz ID if provided (used in the attempts modal)
        quiz_id = self.request.query_params.get('quiz')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        # Filter by student ID if provided
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Handle duplicates: If multiple attempts by same student, only return the latest one
        # unless explicitly asked for all.
        if self.request.query_params.get('latest_only') == 'true':
            
            latest_attempt = queryset.filter(
                student_id=OuterRef('student_id')
            ).order_by('-started_at', '-id').values('id')[:1]
            queryset = queryset.filter(id=Subquery(latest_attempt))

        return queryset.select_related('student', 'quiz', 'quiz__subject').order_by('-started_at')

    def create(self, request, *args, **kwargs):
        return Response(
            {'error': 'Create attempts via /quizzes/{id}/start/ endpoint only.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def _evaluate_attempt(self, attempt):
        _evaluate_attempt(attempt)

    def _close_attempt(self, attempt, close_status):
        _close_attempt(attempt, close_status)

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

        total_marks = attempt.quiz.total_marks
        if not total_marks:
            total_marks = sum((q.marks or Decimal('0')) for q in questions)

        return Response({
            'attempt_id': str(attempt.id),
            'quiz_id': str(attempt.quiz_id),
            'quiz_title': attempt.quiz.title,
            'score': attempt.score,
            'total_marks': total_marks,
            'status': attempt.status,
            'questions': serializer.data
        })


class GradeComponentViewSet(viewsets.ModelViewSet):
    serializer_class = GradeComponentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdminForWrite]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return GradeComponent.objects.none()

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            queryset = GradeComponent.objects.all()
        elif hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            # Teachers only see components for their active subjects
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True, subject__semester__status='active'
            ).values_list('subject_id', flat=True)
            queryset = GradeComponent.objects.filter(subject_id__in=teacher_subjects).select_related('linked_quiz')
        elif hasattr(user, 'student_profile'):
            # Students can see published grade components for their current enrolled subjects
            student = user.student_profile
            enrolled_subjects = StudentSubject.objects.filter(
                student=student,
                subject__semester__number=student.current_semester
            ).values_list('subject_id', flat=True)
            queryset = GradeComponent.objects.filter(
                subject_id__in=enrolled_subjects, 
                is_visible_to_students=True,
                subject__semester__number=student.current_semester
            )
        else:
            return GradeComponent.objects.none()
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
            
        return queryset.distinct()

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'teacher_profile'):
            raise ValidationError('Only teachers can create grade components.')
        
        # Handle assignment linking
        assignment_id = self.request.data.get('assignment_id')
        instance = serializer.save(created_by=self.request.user.teacher_profile)

        if assignment_id:
            try:
                
                assignment = Assignment.objects.get(id=assignment_id)
                
                # Link all existing submissions/grades to this component
                submissions = SubmissionHistory.objects.filter(assignment=assignment)
                for sub in submissions:
                    # Check if there's a grade for this submission
                    try:
                        grade = sub.grade
                        StudentMark.objects.update_or_create(
                            component=instance,
                            student=sub.student,
                            defaults={
                                'marks_obtained': grade.marks_obtained,
                                'remarks': grade.feedback,
                                'graded_by': self.request.user.teacher_profile,
                                'is_locked': True
                            }
                        )
                    except Grade.DoesNotExist:
                        # Just create the record with null marks if no grade exists yet
                        StudentMark.objects.get_or_create(
                            component=instance,
                            student=sub.student,
                            defaults={'marks_obtained': None}
                        )
            except Exception as e:
                logging.getLogger(__name__).error("Error linking assignment marks: %s", e)

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
        if not hasattr(request.user, 'teacher_profile'):
            raise ValidationError('Only teachers can enter marks.')

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
            if created:
                created_count += 1
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
        queryset = queryset.select_related('component', 'component__linked_quiz')
        
        # Authorization filtering
        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            pass
        elif hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            # Teachers only see marks for their active subjects
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True, subject__semester__status='active'
            ).values_list('subject_id', flat=True)
            queryset = queryset.filter(component__subject_id__in=teacher_subjects)
        elif hasattr(user, 'student_profile'):
            # Students only see their own marks from current semester
            student = user.student_profile
            queryset = queryset.filter(
                student=student,
                component__subject__semester__number=student.current_semester
            )
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # 1. Serialize standard StudentMark objects
        serializer = self.get_serializer(queryset, many=True)
        marks_data = serializer.data
        
        # 2. Fetch and include legacy Grade objects (Assignments)
        user = request.user
        legacy_grades_qs = Grade.objects.all().select_related(
            'submission', 'submission__student', 'submission__assignment', 'submission__assignment__subject'
        )
        
        # Apply filters to legacy grades
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            teacher_subjects = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True, subject__semester__status='active'
            ).values_list('subject_id', flat=True)
            legacy_grades_qs = legacy_grades_qs.filter(
                Q(submission__assignment__created_by=teacher) | 
                Q(submission__assignment__subject_id__in=teacher_subjects)
            )
        elif hasattr(user, 'student_profile'):
            student = user.student_profile
            legacy_grades_qs = legacy_grades_qs.filter(
                submission__student=student,
                submission__assignment__subject__semester__number=student.current_semester
            )
        
        subject_id = request.query_params.get('subject')
        if subject_id:
            legacy_grades_qs = legacy_grades_qs.filter(submission__assignment__subject_id=subject_id)
        
        student_id = request.query_params.get('student')
        if student_id:
            legacy_grades_qs = legacy_grades_qs.filter(submission__student_id=student_id)
        
        # Serialize legacy grades manually or with custom structure
        for g in legacy_grades_qs:
            assignment = g.submission.assignment
            st_profile = g.submission.student
            
            # Check if this assignment is already represented by a StudentMark to avoid duplicates
            if any(
                (m.get('component_name') == assignment.title or m.get('assignment_title') == assignment.title) and 
                float(m.get('marks_obtained') or 0) == float(g.marks_obtained or 0) and 
                float(m.get('total_marks') or 0) == float(assignment.total_marks or 0)
                for m in marks_data
            ):
                continue

            marks_data.append({
                'id': str(g.id),
                'student_id': str(st_profile.id),
                'student_name': st_profile.full_name,
                'student_roll_no': st_profile.enrollment_number,
                'component_name': assignment.title,
                'component_type': 'assignment',
                'marks_obtained': float(g.marks_obtained or 0),
                'max_marks': float(assignment.total_marks or 0),
                'weightage': 10.00, # Default weight for legacy assignments
                'percentage': round((float(g.marks_obtained or 0) / float(assignment.total_marks or 1)) * 100, 2) if assignment.total_marks else 0,
                'is_locked': True,
                'graded_at': g.graded_at.isoformat() if g.graded_at else None
            })
            
        return Response(marks_data)


# ── Subject Result (Pass/Fail) ViewSet ──────────────────────────────────────

from ..models.academic import SubjectResult, Subject, Semester
from ..models.grading import GradingScheme, StudentGradeSummary
from ..serializers.grading import SubjectResultSerializer, SubjectResultBulkSerializer


class SubjectResultViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student subject pass/fail results."""
    serializer_class = SubjectResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    PASSING_THRESHOLD = 40  # Default fallback

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy',
                           'bulk_update', 'initialize', 'auto_calculate'):
            return [permissions.IsAuthenticated(), IsAdminOrTeacher()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return SubjectResult.objects.none()

        qs = SubjectResult.objects.select_related(
            'student', 'subject', 'semester', 'decided_by'
        )

        if user.is_staff or user.is_superuser or hasattr(user, 'admin_profile'):
            pass
        elif hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            teacher_subject_ids = TeacherSubject.objects.filter(
                teacher=teacher, is_active=True
            ).values_list('subject_id', flat=True)
            qs = qs.filter(subject_id__in=teacher_subject_ids)
        elif hasattr(user, 'student_profile'):
            qs = qs.filter(student=user.student_profile)
        else:
            return SubjectResult.objects.none()

        # Query param filters
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        semester_id = self.request.query_params.get('semester')
        if semester_id:
            qs = qs.filter(semester_id=semester_id)

        student_id = self.request.query_params.get('student')
        if student_id:
            qs = qs.filter(student_id=student_id)

        return qs.order_by('student__full_name', 'subject__code')

    def _get_passing_threshold(self, subject):
        """Get passing marks threshold from GradingScheme for this subject."""
        scheme = GradingScheme.objects.filter(subject=subject).first()
        if not scheme:
            scheme = GradingScheme.objects.filter(is_default=True).first()
        return float(scheme.passing_marks) if scheme else self.PASSING_THRESHOLD

    def _get_letter_grade(self, percentage):
        """Calculate letter grade from percentage."""
        if percentage >= 90: return 'A+'
        if percentage >= 85: return 'A'
        if percentage >= 80: return 'A-'
        if percentage >= 75: return 'B+'
        if percentage >= 70: return 'B'
        if percentage >= 65: return 'B-'
        if percentage >= 60: return 'C+'
        if percentage >= 55: return 'C'
        if percentage >= 50: return 'C-'
        if percentage >= 40: return 'D'
        return 'F'

    def _calc_student_percentage(self, student, subject):
        """Calculate weighted percentage for a student in a subject from StudentMark data."""
        marks = StudentMark.objects.filter(
            student=student, component__subject=subject
        ).select_related('component')

        total_weighted = Decimal('0')
        total_weight = Decimal('0')

        for mark in marks:
            max_marks = Decimal(str(mark.component.max_marks or 0))
            obtained = Decimal(str(mark.marks_obtained or 0))
            weight = Decimal(str(mark.component.weightage or 0))

            if max_marks > 0:
                pct = (obtained / max_marks) * 100
                total_weighted += pct * weight / 100
                total_weight += weight

        if total_weight > 0:
            return float((total_weighted / total_weight) * 100)

        # Fallback: simple average if no weightage
        if marks.exists():
            total_obtained = sum(float(m.marks_obtained or 0) for m in marks)
            total_max = sum(float(m.component.max_marks or 0) for m in marks)
            if total_max > 0:
                return round((total_obtained / total_max) * 100, 2)

        return 0.0

    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Create pending SubjectResult entries for all students enrolled in a subject."""
        subject_id = request.data.get('subject') or request.data.get('subject_id')

        if not subject_id:
            return Response({'error': 'subject ID is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subject = get_object_or_404(Subject, id=subject_id)
        semester = subject.semester

        if not semester:
            return Response({'error': 'Subject is not linked to a semester.'},
                            status=status.HTTP_400_BAD_REQUEST)

        enrollments = StudentSubject.objects.filter(subject=subject)
        created_count = 0

        for enrollment in enrollments:
            _, created = SubjectResult.objects.get_or_create(
                student=enrollment.student,
                subject=subject,
                semester=semester,
                defaults={'result': 'pending'}
            )
            if created:
                created_count += 1

        return Response({
            'status': 'success',
            'created': created_count,
            'total_enrolled': enrollments.count()
        })

    @action(detail=False, methods=['post'])
    def auto_calculate(self, request):
        """Auto-calculate pass/fail for all students in a subject."""
        subject_id = request.data.get('subject') or request.data.get('subject_id')

        if not subject_id:
            return Response({'error': 'subject ID is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subject = get_object_or_404(Subject, id=subject_id)
        semester = subject.semester
        
        if not semester:
            return Response({'error': 'Subject is not linked to a semester.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1. Sync QuizAttempts & SubmissionHistory grades to StudentMark first!
        from lms_cors.models import Quiz, QuizAttempt
        from lms_cors.models.assignments import Assignment, SubmissionHistory, Grade

        components = GradeComponent.objects.filter(subject=subject)
        for comp in components:
            if comp.component_type == 'quiz':
                try:
                    linked_quiz = comp.linked_quiz
                except Exception:
                    linked_quiz = None

                if linked_quiz:
                    attempts = QuizAttempt.objects.filter(quiz=linked_quiz, status='completed')
                for attempt in attempts:
                    StudentMark.objects.update_or_create(
                        component=comp,
                        student=attempt.student,
                        defaults={
                            'marks_obtained': Decimal(str(attempt.score or 0)),
                            'is_locked': True
                        }
                    )
            elif comp.component_type == 'assignment':
                a_obj = Assignment.objects.filter(title=comp.name, subject=subject).first()
                if a_obj:
                    submissions = SubmissionHistory.objects.filter(assignment=a_obj)
                    for sub in submissions:
                        try:
                            grade = sub.grade
                            StudentMark.objects.update_or_create(
                                component=comp,
                                student=sub.student,
                                defaults={
                                    'marks_obtained': Decimal(str(grade.marks_obtained or 0)),
                                    'is_locked': True
                                }
                            )
                        except Grade.DoesNotExist:
                            pass

        # 2. Iterate through SubjectResults and calculate midterm (40) and sessional (60)
        results = SubjectResult.objects.filter(subject=subject, semester=semester)
        updated_count = 0

        for result in results:
            # Fetch all StudentMark entries for this subject
            student_marks = StudentMark.objects.filter(
                student=result.student, component__subject=subject
            ).select_related('component')

            # Calculate Mid Term marks (out of 40) - Split by categories:
            # - Quizzes: max 10 marks
            # - Assignments: max 10 marks
            # - Midterm paper: max 20 marks
            # - Total = 40 marks
            
            # 1. Quizzes (out of 10)
            quiz_list = [m for m in student_marks if m.component.component_type == 'quiz']
            quiz_val = Decimal('0')
            if quiz_list:
                quiz_weighted = Decimal('0')
                quiz_weight_sum = Decimal('0')
                for m in quiz_list:
                    max_m = Decimal(str(m.component.max_marks or 0))
                    obt = Decimal(str(m.marks_obtained or 0))
                    w = Decimal(str(m.component.weightage or 0))
                    if max_m > 0:
                        pct = (obt / max_m) * Decimal('100')
                        quiz_weighted += pct * w / Decimal('100')
                        quiz_weight_sum += w
                if quiz_weight_sum > 0:
                    quiz_pct = (quiz_weighted / quiz_weight_sum) * Decimal('100')
                    quiz_val = (quiz_pct / Decimal('100')) * Decimal('10')
                else:
                    quiz_max = sum(Decimal(str(m.component.max_marks or 0)) for m in quiz_list)
                    quiz_obt = sum(Decimal(str(m.marks_obtained or 0)) for m in quiz_list)
                    if quiz_max > 0:
                        quiz_val = (quiz_obt / quiz_max) * Decimal('10')

            # 2. Assignments (out of 10)
            assignment_list = [m for m in student_marks if m.component.component_type == 'assignment']
            assignment_val = Decimal('0')
            if assignment_list:
                assignment_weighted = Decimal('0')
                assignment_weight_sum = Decimal('0')
                for m in assignment_list:
                    max_m = Decimal(str(m.component.max_marks or 0))
                    obt = Decimal(str(m.marks_obtained or 0))
                    w = Decimal(str(m.component.weightage or 0))
                    if max_m > 0:
                        pct = (obt / max_m) * Decimal('100')
                        assignment_weighted += pct * w / Decimal('100')
                        assignment_weight_sum += w
                if assignment_weight_sum > 0:
                    assignment_pct = (assignment_weighted / assignment_weight_sum) * Decimal('100')
                    assignment_val = (assignment_pct / Decimal('100')) * Decimal('10')
                else:
                    assignment_max = sum(Decimal(str(m.component.max_marks or 0)) for m in assignment_list)
                    assignment_obt = sum(Decimal(str(m.marks_obtained or 0)) for m in assignment_list)
                    if assignment_max > 0:
                        assignment_val = (assignment_obt / assignment_max) * Decimal('10')

            # 3. Midterm Paper (out of 20)
            midterm_paper_list = [m for m in student_marks if m.component.component_type == 'midterm']
            if result.mid_paper_marks is not None:
                midterm_paper_val = result.mid_paper_marks
            else:
                midterm_paper_val = Decimal('0')
                if midterm_paper_list:
                    mid_weighted = Decimal('0')
                    mid_weight_sum = Decimal('0')
                    for m in midterm_paper_list:
                        max_m = Decimal(str(m.component.max_marks or 0))
                        obt = Decimal(str(m.marks_obtained or 0))
                        w = Decimal(str(m.component.weightage or 0))
                        if max_m > 0:
                            pct = (obt / max_m) * Decimal('100')
                            mid_weighted += pct * w / Decimal('100')
                            mid_weight_sum += w
                    if mid_weight_sum > 0:
                        mid_pct = (mid_weighted / mid_weight_sum) * Decimal('100')
                        midterm_paper_val = (mid_pct / Decimal('100')) * Decimal('20')
                    else:
                        mid_max = sum(Decimal(str(m.component.max_marks or 0)) for m in midterm_paper_list)
                        mid_obt = sum(Decimal(str(m.marks_obtained or 0)) for m in midterm_paper_list)
                        if mid_max > 0:
                            midterm_paper_val = (mid_obt / mid_max) * Decimal('20')

            # Midterm Val is the sum of Quizzes (10) + Assignments (10) + Midterm Exam (20) = 40 max
            mid_val = quiz_val + assignment_val + midterm_paper_val

            # Sessional is not calculated by the system; keep the teacher's manually entered sessional marks
            sess_val = result.sessional_marks or Decimal('0')
            total_val = mid_val + sess_val

            scheme = GradingScheme.objects.filter(subject=subject).first()
            if not scheme:
                scheme = GradingScheme.objects.filter(is_default=True).first()

            percentage_float = float(total_val)
            letter_grade = 'F'
            if scheme:
                if percentage_float >= float(scheme.a_plus_min): letter_grade = 'A+'
                elif percentage_float >= float(scheme.a_min): letter_grade = 'A'
                elif percentage_float >= float(scheme.a_minus_min): letter_grade = 'A-'
                elif percentage_float >= float(scheme.b_plus_min): letter_grade = 'B+'
                elif percentage_float >= float(scheme.b_min): letter_grade = 'B'
                elif percentage_float >= float(scheme.b_minus_min): letter_grade = 'B-'
                elif percentage_float >= float(scheme.c_plus_min): letter_grade = 'C+'
                elif percentage_float >= float(scheme.c_min): letter_grade = 'C'
                elif percentage_float >= float(scheme.c_minus_min): letter_grade = 'C-'
                elif percentage_float >= float(scheme.d_min): letter_grade = 'D'
            else:
                if percentage_float >= 90: letter_grade = 'A+'
                elif percentage_float >= 85: letter_grade = 'A'
                elif percentage_float >= 80: letter_grade = 'A-'
                elif percentage_float >= 75: letter_grade = 'B+'
                elif percentage_float >= 70: letter_grade = 'B'
                elif percentage_float >= 65: letter_grade = 'B-'
                elif percentage_float >= 60: letter_grade = 'C+'
                elif percentage_float >= 55: letter_grade = 'C'
                elif percentage_float >= 50: letter_grade = 'C-'
                elif percentage_float >= 40: letter_grade = 'D'

            gpa_map = {
                'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
            }
            gpa_val = gpa_map.get(letter_grade, 0.0)

            result.mid_paper_marks = Decimal(str(round(midterm_paper_val, 2)))
            result.mid_marks = Decimal(str(round(mid_val, 2)))
            result.sessional_marks = Decimal(str(round(sess_val, 2)))
            result.total_marks = Decimal(str(round(total_val, 2)))
            result.percentage = result.total_marks
            result.letter_grade = letter_grade
            result.result = 'pass' if percentage_float >= 50.0 else 'fail'
            result.gpa = Decimal(str(gpa_val))
            result.is_overridden = False
            result.save()
            updated_count += 1

        return Response({
            'status': 'success',
            'updated': updated_count,
            'passing_threshold': 50.0
        })

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update pass/fail results by SubjectResult ID."""
        if not hasattr(request.user, 'teacher_profile') and not request.user.is_staff:
            return Response({'error': 'Only teachers and admins can update results.'},
                            status=status.HTTP_403_FORBIDDEN)

        results_data = request.data.get('results', [])
        if not results_data:
            return Response({'error': 'No results provided.'}, status=status.HTTP_400_BAD_REQUEST)

        teacher = getattr(request.user, 'teacher_profile', None)
        updated_count = 0

        with transaction.atomic():
            for item in results_data:
                result_id = item.get('id')
                if not result_id:
                    continue
                
                try:
                    res_obj = SubjectResult.objects.get(id=result_id)
                    mid_paper_marks = item.get('mid_paper_marks')
                    mid_marks = item.get('mid_marks')
                    sessional_marks = item.get('sessional_marks')

                    if mid_paper_marks is not None:
                        res_obj.mid_paper_marks = Decimal(str(mid_paper_marks)) if mid_paper_marks != '' else None
                    elif mid_marks is not None:
                        res_obj.mid_paper_marks = Decimal(str(mid_marks)) if mid_marks != '' else None

                    if sessional_marks is not None:
                        res_obj.sessional_marks = Decimal(str(sessional_marks)) if sessional_marks != '' else None

                    # If mid_paper_marks is provided, res_obj.save() will calculate the new mid_marks.
                    # We save the object first to ensure the save() calculations run.
                    res_obj.save()

                    # Automatically calculate total, percentage, grade, gpa and result if marks exist
                    if res_obj.mid_marks is not None or res_obj.sessional_marks is not None:
                        mid_val = res_obj.mid_marks or Decimal('0')
                        sess_val = res_obj.sessional_marks or Decimal('0')
                        res_obj.total_marks = mid_val + sess_val
                        res_obj.percentage = res_obj.total_marks

                        scheme = GradingScheme.objects.filter(subject=res_obj.subject).first()
                        if not scheme:
                            scheme = GradingScheme.objects.filter(is_default=True).first()

                        percentage_float = float(res_obj.percentage)
                        letter_grade = 'F'
                        if scheme:
                            if percentage_float >= float(scheme.a_plus_min): letter_grade = 'A+'
                            elif percentage_float >= float(scheme.a_min): letter_grade = 'A'
                            elif percentage_float >= float(scheme.a_minus_min): letter_grade = 'A-'
                            elif percentage_float >= float(scheme.b_plus_min): letter_grade = 'B+'
                            elif percentage_float >= float(scheme.b_min): letter_grade = 'B'
                            elif percentage_float >= float(scheme.b_minus_min): letter_grade = 'B-'
                            elif percentage_float >= float(scheme.c_plus_min): letter_grade = 'C+'
                            elif percentage_float >= float(scheme.c_min): letter_grade = 'C'
                            elif percentage_float >= float(scheme.c_minus_min): letter_grade = 'C-'
                            elif percentage_float >= float(scheme.d_min): letter_grade = 'D'
                        else:
                            if percentage_float >= 90: letter_grade = 'A+'
                            elif percentage_float >= 85: letter_grade = 'A'
                            elif percentage_float >= 80: letter_grade = 'A-'
                            elif percentage_float >= 75: letter_grade = 'B+'
                            elif percentage_float >= 70: letter_grade = 'B'
                            elif percentage_float >= 65: letter_grade = 'B-'
                            elif percentage_float >= 60: letter_grade = 'C+'
                            elif percentage_float >= 55: letter_grade = 'C'
                            elif percentage_float >= 50: letter_grade = 'C-'
                            elif percentage_float >= 40: letter_grade = 'D'

                        res_obj.letter_grade = letter_grade
                        
                        gpa_map = {
                            'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                            'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
                        }
                        res_obj.gpa = Decimal(str(gpa_map.get(letter_grade, 0.0)))
                        
                        # "under 50 fail" threshold
                        res_obj.result = 'pass' if percentage_float >= 50.0 else 'fail'

                    # Teacher custom result selection has precedence (explicit control)
                    custom_result = item.get('result')
                    if custom_result in ['pass', 'fail']:
                        res_obj.result = custom_result
                        res_obj.is_overridden = True

                    res_obj.remarks = item.get('remarks', res_obj.remarks)
                    res_obj.decided_by = teacher
                    res_obj.decided_at = timezone.now()
                    res_obj.save()
                    updated_count += 1
                except SubjectResult.DoesNotExist:
                    continue

        return Response({'status': 'success', 'updated': updated_count})
