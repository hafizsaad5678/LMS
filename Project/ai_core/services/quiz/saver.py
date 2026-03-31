import json
from datetime import timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from ai_core.services.config import (
    QUIZ_DUPLICATE_WINDOW_SECONDS,
    QUIZ_GRADE_COMPONENT_STATUS,
    QUIZ_GRADE_COMPONENT_WEIGHTAGE,
)
from lms_cors.models.academic import Subject
from lms_cors.models.grading import (
    GradeComponent,
    Quiz,
    QuizAttempt,
    QuizOption,
    QuizQuestion,
    StudentMark,
)
from lms_cors.models.people import Student, StudentSubject, Teacher


class QuizSaveService:
    @staticmethod
    def save_quiz(validated_data: dict, user):
        recent_time = timezone.now() - timedelta(seconds=QUIZ_DUPLICATE_WINDOW_SECONDS)
        existing_quiz = Quiz.objects.filter(
            title=validated_data["title"],
            subject_id=validated_data["subject_id"],
            created_by__user=user,
            created_at__gte=recent_time,
        ).first()

        if existing_quiz:
            return {
                "message": "Duplicate quiz submission detected. Returning existing record.",
                "quiz_id": str(existing_quiz.id),
                "already_exists": True,
            }, 200

        subject = Subject.objects.get(id=validated_data["subject_id"])
        teacher = Teacher.objects.get(user=user)
        quiz_json = validated_data["quiz_data"]

        grade_comp = GradeComponent.objects.create(
            subject=subject,
            created_by=teacher,
            name=validated_data["title"],
            component_type="quiz",
            max_marks=quiz_json.get("total_marks", 0),
            weightage=QUIZ_GRADE_COMPONENT_WEIGHTAGE,
            status=QUIZ_GRADE_COMPONENT_STATUS,
        )

        quiz = Quiz.objects.create(
            title=validated_data["title"],
            description=validated_data.get("description", ""),
            subject=subject,
            created_by=teacher,
            grade_component=grade_comp,
            is_published=True,
        )

        q_type_map = {
            "MCQ": "mcq",
            "Short Answer": "short_answer",
            "Long Answer": "essay",
            # "Mixed" should be decomposed by the generator into concrete question types.
            # If it leaks through at item-level, default to MCQ for backward compatibility.
            "Mixed": "mcq",
        }

        for q_data in quiz_json.get("questions", []):
            question = QuizQuestion.objects.create(
                quiz=quiz,
                question_text=q_data["question_text"],
                question_type=q_type_map.get(q_data.get("question_type", "MCQ"), "mcq"),
                marks=q_data.get("marks", 1),
                correct_answer_text=q_data.get("correct_answer_text", q_data.get("correct_answer", "")),
                explanation=q_data.get("explanation", ""),
            )

            if q_data.get("question_type", "MCQ") == "MCQ":
                for opt_data in q_data.get("options", []):
                    if isinstance(opt_data, dict):
                        text = opt_data.get("text", "")
                        is_correct = opt_data.get("is_correct", False)
                    else:
                        text = opt_data
                        is_correct = text == q_data.get("correct_answer")

                    QuizOption.objects.create(
                        question=question,
                        option_text=text,
                        is_correct=is_correct,
                    )

        assign_mode = validated_data.get("assign_mode", "all")
        target_ids = validated_data.get("target_ids", [])

        assigned_students = []
        if assign_mode == "all":
            student_subjects = StudentSubject.objects.filter(subject=subject)
            assigned_students = [ss.student for ss in student_subjects]
        elif assign_mode == "department":
            student_subjects = StudentSubject.objects.filter(subject=subject).select_related(
                "student", "student__program"
            )
            assigned_students = [
                ss.student
                for ss in student_subjects
                if ss.student.program
                and ss.student.program.department_id
                and ss.student.program.department_id in target_ids
            ]
        elif assign_mode == "students":
            assigned_students = list(Student.objects.filter(id__in=target_ids))

        assignment_metadata = {
            "assign_mode": assign_mode,
            "target_ids": target_ids,
            "deadline": validated_data.get("deadline"),
        }
        quiz.description = json.dumps(assignment_metadata, cls=DjangoJSONEncoder)
        quiz.save()

        for student in assigned_students:
            QuizAttempt.objects.get_or_create(quiz=quiz, student=student)
            StudentMark.objects.get_or_create(component=grade_comp, student=student)

        return {
            "message": "Quiz generated and assigned successfully",
            "quiz_id": str(quiz.id),
            "assigned_count": len(assigned_students),
        }, 201
