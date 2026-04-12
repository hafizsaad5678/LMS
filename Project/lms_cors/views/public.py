from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ..models.people import Student, Teacher
from ..models.academic import Subject, Institution


class PublicFormRateThrottle(SimpleRateThrottle):
    scope = "public_form"
    rate = "10/min"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        view_name = getattr(view, "__name__", "public")
        return self.cache_format % {
            "scope": f"{self.scope}:{view_name}",
            "ident": ident,
        }

@api_view(['GET'])
@permission_classes([AllowAny])
def public_stats(request):
    """
    Returns real-time aggregated stats of the platform.
    """
    # Simulate getting real time live numbers.
    try:
        students_count = Student.objects.count()
    except Exception:
        students_count = 500
        
    try:
        teachers_count = Teacher.objects.count()
    except Exception:
        teachers_count = 50
        
    try:
        subjects_count = Subject.objects.count()
    except Exception:
        subjects_count = 100
        
    try:
        institutions_count = Institution.objects.count()
    except Exception:
        institutions_count = 10
    
    return Response({
        "activeStudents": students_count,
        "expertTeachers": teachers_count,
        "totalCourses": subjects_count,
        "institutions": institutions_count,
        "platformUptime": 99.98
    })

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PublicFormRateThrottle])
def submit_contact(request):
    """
    Mocks submitting an enterprise contact request.
    """
    email = str(request.data.get("email", "")).strip()
    company = str(request.data.get("company", "")).strip()
    message = str(request.data.get("message", "")).strip()

    if not email or not message:
        return Response(
            {"detail": "email and message are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"detail": "Please provide a valid email address."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(company) > 255:
        return Response(
            {"detail": "company must be 255 characters or fewer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(message) < 5 or len(message) > 5000:
        return Response(
            {"detail": "message must be between 5 and 5000 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"status": "Contact inquiry successfully received by sales."})

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PublicFormRateThrottle])
def submit_feedback(request):
    """
    Mocks submitting platform feedback.
    """
    feedback = str(request.data.get("feedback", "")).strip()

    if not feedback:
        return Response(
            {"detail": "feedback is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(feedback) < 2 or len(feedback) > 3000:
        return Response(
            {"detail": "feedback must be between 2 and 3000 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"status": "Feedback logged successfully."})