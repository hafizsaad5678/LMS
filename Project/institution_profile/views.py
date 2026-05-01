from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Institution
from lms_cors.models import Program
from .serializers import InstitutionPublicProfileSerializer
from django.core.mail import send_mail
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def institution_profile_view(request, slug):
    """Public institution profile by slug with optimized fetching."""
    print(f"DEBUG: institution_profile_view hit with slug: {slug}")
    
    # Pre-fetch all related data in minimum queries to avoid N+1 slowness
    institution = get_object_or_404(
        Institution.objects.prefetch_related(
            'departments',
            'departments__programs',
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
    print(f"DEBUG: public_admission_inquiry hit with method {request.method}")
    if request.method == 'GET':
        return Response({'status': 'ok', 'message': 'Endpoint is reachable'})
        
    data = request.data
    program_id = data.get('program_id')
    
    if not program_id:
        return Response({'error': 'Program ID is required'}, status=400)
        
    program = get_object_or_404(Program, id=program_id)
    department = program.department
    institution = department.institution
    
    # Target email: Dept email first, then Institution email
    target_email = department.email or institution.email or settings.DEFAULT_FROM_EMAIL
    
    # Construct Email
    subject = f"New Admission Inquiry: {program.name} - {data.get('name')}"
    message = f"""
    New admission inquiry received for {program.name}.
    
    Student Details:
    ----------------
    Full Name: {data.get('name')}
    Father's Name: {data.get('father_name')}
    Phone Number: {data.get('phone')}
    Email Address: {data.get('email')}
    
    Interested Program: {program.name} ({department.name} Department)
    
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
        # We log and return success anyway for now to avoid blocking the user if email is not configured
        print(f"Email error: {e}")
        return Response({'status': 'partial_success', 'message': 'Inquiry received but email failed to send.'})
