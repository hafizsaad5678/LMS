from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Institution
from django.db.models import Prefetch, Q
from lms_cors.models import Program, Department, AcademicSession
from .serializers import InstitutionPublicProfileSerializer
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def institution_profile_view(request, slug):
    """Public institution profile by slug with optimized fetching."""
    
    # Pre-fetch all related data in minimum queries to avoid N+1 slowness
    institution = get_object_or_404(
        Institution.objects.prefetch_related(
            Prefetch('departments', queryset=Department.objects.filter(is_active=True)),
            'departments__programs',
            Prefetch('departments__programs__sessions', queryset=AcademicSession.objects.filter(is_active=True)),
            'departments__programs__semesters_legacy',
            'departments__programs__semesters_legacy__subjects',
            'gallery_images',
            'features',
            'testimonials',
            'events',
            'admissions',
            'contacts'
        ), 
        slug=slug, 
        is_active=True
    )
    
    serializer = InstitutionPublicProfileSerializer(institution, context={'request': request})
    return Response(serializer.data)

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def public_admission_inquiry(request):
    """Handle student admission inquiry and notify department."""
    if request.method == 'GET':
        return Response({'status': 'ok', 'message': 'Endpoint is reachable'})
        
    data = request.data
    program_id = data.get('program_id')
    institution_id = data.get('institution_id')
    
    # Target and subject defaults
    target_email = None
    subject_program = "General Inquiry"
    body_program = "General/Featured Admission"
    remarks = data.get('remarks', 'No additional remarks.')

    if program_id:
        try:
            program = Program.objects.get(id=program_id)
            department = program.department
            institution = department.institution
            target_email = department.email or institution.email
            subject_program = program.name
            body_program = f"{program.name} ({department.name} Department)"
        except (Program.DoesNotExist, ValueError):
            # If program_id is invalid (like 'featured:Title'), fallback to institution
            pass

    if not target_email and institution_id:
        institution = get_object_or_404(Institution, id=institution_id)
        target_email = institution.email
    
    if not target_email:
        target_email = settings.DEFAULT_FROM_EMAIL

    # Validate and sanitize user inputs
    name = str(data.get('name', '')).strip()[:200]
    father_name = str(data.get('father_name', '')).strip()[:200]
    phone = str(data.get('phone', '')).strip()[:20]
    email_input = str(data.get('email', '')).strip()[:254]

    if not name or not email_input:
        return Response({'error': 'Name and email are required'}, status=400)

    try:
        validate_email(email_input)
    except ValidationError:
        return Response({'error': 'Please provide a valid email address'}, status=400)
    
    # Construct Email with sanitized inputs
    subject = f"New Admission Inquiry: {subject_program} - {name}"
    message = f"""
    New admission inquiry received for {subject_program}.
    
    Student Details:
    ----------------
    Full Name: {name}
    Father's Name: {father_name}
    Phone Number: {phone}
    Email Address: {email_input}
    
    Interested In: {body_program}
    Additional Remarks: {remarks}
    
    This inquiry was sent via the Institution Public Profile.
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [target_email],
            fail_silently=False,
        )
        return Response({'status': 'success', 'message': 'Inquiry sent successfully'})
    except Exception as e:
        logger.error("Email error in admission inquiry: %s", e)
        return Response({'status': 'partial_success', 'message': 'Inquiry received but email failed to send.'})
