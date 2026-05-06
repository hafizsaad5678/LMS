from rest_framework import serializers
from django.db.models import Q
from django.utils import timezone
from .models import (
    Institution, InstitutionGallery, InstitutionFeature, InstitutionEvent,
    InstitutionAdmissionInfo, InstitutionContact, InstitutionTestimonial,
    InstitutionAdmissionFeatured
)
from lms_cors.models import Department, Program, Teacher, Event, AcademicSession

class InstitutionGallerySerializer(serializers.ModelSerializer):
    """Serializer for institution gallery images."""

    class Meta:
        model = InstitutionGallery
        fields = ['id', 'image', 'category', 'caption', 'is_featured', 'order']
        read_only_fields = ['id']


class InstitutionFeatureSerializer(serializers.ModelSerializer):
    """Serializer for institution feature cards."""

    class Meta:
        model = InstitutionFeature
        fields = ['id', 'title', 'description', 'icon', 'order']
        read_only_fields = ['id']


class InstitutionEventSerializer(serializers.ModelSerializer):
    """Serializer for institution events."""

    class Meta:
        model = InstitutionEvent
        fields = ['id', 'title', 'description', 'event_date', 'location', 'order']
        read_only_fields = ['id']


class InstitutionAdmissionInfoSerializer(serializers.ModelSerializer):
    """Serializer for simple admissions info section."""

    class Meta:
        model = InstitutionAdmissionInfo
        fields = ['id', 'title', 'description', 'apply_url', 'apply_email']
        read_only_fields = ['id']


class InstitutionAdmissionFeaturedSerializer(serializers.ModelSerializer):
    """Serializer for featured admission promotional cards."""
    class Meta:
        model = InstitutionAdmissionFeatured
        fields = ['id', 'title', 'description', 'image', 'badge_text', 'link_url', 'admission_start_date', 'admission_end_date', 'order']
        read_only_fields = ['id']


class InstitutionContactSerializer(serializers.ModelSerializer):
    """Serializer for institution contact blocks."""

    class Meta:
        model = InstitutionContact
        fields = ['id', 'title', 'description', 'email', 'phone', 'website', 'address']
        read_only_fields = ['id']


class InstitutionTestimonialSerializer(serializers.ModelSerializer):
    """Serializer for institution testimonials."""
    class Meta:
        model = InstitutionTestimonial
        fields = ['id', 'name', 'role', 'content', 'profile_image', 'rating', 'order']
        read_only_fields = ['id']


class InstitutionPublicTeacherSerializer(serializers.ModelSerializer):
    """Minimal teacher data for public institution profile."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'designation', 'profile_image', 'department_name', 'specialization']
        read_only_fields = ['id']


class InstitutionPublicProgramSerializer(serializers.ModelSerializer):
    """Program data with curriculum for public profile."""
    curriculum = serializers.SerializerMethodField()
    admission_sessions = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            'id', 'name', 'description', 'program_level', 
            'duration_years', 'min_credit_hours', 'curriculum',
            'academic_system', 'requires_thesis', 'requires_internship',
            'admission_sessions'
        ]
        read_only_fields = ['id']

    def get_curriculum(self, obj):
        # Fetch semesters associated with this program
        # Note: semesters_legacy is prefetched in the view
        semesters = sorted(obj.semesters_legacy.all(), key=lambda x: x.number)
        data = []
        for sem in semesters:
            # subjects is prefetched in the view
            subjects = sem.subjects.all()
            data.append({
                'semester_number': sem.number,
                'semester_name': sem.name,
                'subjects': [
                    {'name': s.name, 'code': s.code, 'credits': s.credit_hours} 
                    for s in subjects
                ]
            })
        return data

    def get_admission_sessions(self, obj):
        sessions = obj.sessions.filter(is_active=True).filter(
            Q(admission_start_date__isnull=False) | Q(admission_end_date__isnull=False)
        ).order_by('-start_year')
        return ProgramAdmissionSerializer(sessions, many=True).data


class ProgramAdmissionSerializer(serializers.ModelSerializer):
    """Admission window details for a program session."""
    admissions_open = serializers.SerializerMethodField()

    class Meta:
        model = AcademicSession
        fields = [
            'id', 'session_name', 'session_code', 'start_year', 'end_year',
            'admission_start_date', 'admission_end_date', 'status', 'is_active',
            'admissions_open'
        ]
        read_only_fields = ['id']

    def get_admissions_open(self, obj):
        today = timezone.now().date()
        start_date = obj.admission_start_date
        end_date = obj.admission_end_date

        if start_date and end_date:
            return start_date <= today <= end_date
        if start_date and not end_date:
            return today >= start_date
        if end_date and not start_date:
            return today <= end_date
        return False


class InstitutionPublicDepartmentSerializer(serializers.ModelSerializer):
    """Minimal department data for public institution profile."""
    programs = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'image', 'programs',
            'head_of_department', 'email', 'phone', 'vision', 'mission',
            'academic_focus', 'facilities'
        ]
        read_only_fields = ['id']
        
    def get_programs(self, obj):
        return InstitutionPublicProgramSerializer(obj.programs.all(), many=True).data


class InstitutionPublicProfileSerializer(serializers.ModelSerializer):
    """Public-facing institution profile with linked data."""
    departments = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    admissions = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    all_contacts = serializers.SerializerMethodField()
    featured_admissions = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'slug', 'short_name', 'established_year',
            'description', 'mission', 'vision', 'tagline', 'footer_text',
            'show_admissions',
            'email', 'phone', 'website', 'city', 'state', 'country',
            'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url',
            'logo', 'cover_image', 'theme_color', 'secondary_color',
            'principal_name', 'principal_image', 'principal_message',
            'departments', 'gallery', 'features', 'events', 'admissions', 'contact', 
            'all_contacts', 'faculty', 'testimonials', 'featured_admissions'
        ]
        read_only_fields = ['id']

    def get_departments(self, obj):
        # Use in-memory filtering for prefetched data
        departments = [d for d in obj.departments.all() if d.is_active]
        return InstitutionPublicDepartmentSerializer(departments, many=True).data

    def get_gallery(self, obj):
        return InstitutionGallerySerializer(obj.gallery_images.all(), many=True).data

    def get_features(self, obj):
        features = obj.features.filter(is_active=True)
        return InstitutionFeatureSerializer(features, many=True).data

    def get_events(self, obj):
        # 1. Try to get specific branding events
        events = list(obj.events.filter(is_active=True))
        
        # 2. If no branding events, fallback to general academic events
        if not events:
            from django.utils import timezone
            # Fetch 6 upcoming academic events
            academic_events = Event.objects.filter(
                is_active=True,
                event_date__gte=timezone.now().date()
            ).order_by('event_date')[:6]
            
            # Map them to a compatible format for the frontend
            return [{
                'id': str(e.id),
                'title': e.title,
                'description': e.description,
                'event_date': e.event_date,
                'location': e.location or 'Main Campus'
            } for e in academic_events]
            
        return InstitutionEventSerializer(events, many=True).data

    def get_admissions(self, obj):
        # 1. Try to get manual branding admissions info
        admissions = obj.admissions.filter(is_active=True).first()
        if admissions:
            return InstitutionAdmissionInfoSerializer(admissions).data
            
        # 2. Fallback: Check for active program admission sessions
        from lms_cors.models import AcademicSession
        from django.utils import timezone
        today = timezone.now().date()
        
        # Find any session with an open admission window for this institution
        open_session = AcademicSession.objects.filter(
            program__department__institution=obj,
            is_active=True,
            admission_start_date__lte=today,
            admission_end_date__gte=today
        ).select_related('program').first()
        
        if open_session:
            return {
                'id': 'fallback-open',
                'title': f'Admissions Open: {open_session.session_name or open_session.start_year}',
                'description': f'General admissions are currently active for the upcoming academic session. You can now apply for various programs including {open_session.program.name}. Please follow the guidelines below to proceed with your application.',
                'apply_url': obj.website,
                'apply_email': obj.email
            }
            
        return None

    def get_contact(self, obj):
        contact = obj.contacts.order_by('-is_primary', 'order', 'created_at').first()
        if not contact:
            return None
        return InstitutionContactSerializer(contact).data

    def get_all_contacts(self, obj):
        # 1. Start with dedicated institution contacts (Address, etc.)
        contacts_data = InstitutionContactSerializer(
            obj.contacts.order_by('-is_primary', 'order', 'created_at'), 
            many=True
        ).data
        
        # 2. Add Main Institution Phone if not already present
        if obj.phone and not any(c.get('phone') == obj.phone for c in contacts_data):
            contacts_data.insert(0, {
                'id': 'inst-phone',
                'title': 'College Office',
                'phone': obj.phone,
                'email': None,
                'address': None
            })
        
        # 3. Add Department Phone Numbers
        departments = obj.departments.filter(is_active=True)
        for dept in departments:
            if dept.phone:
                contacts_data.append({
                    'id': f'dept-{dept.id}',
                    'title': f'{dept.name} Department',
                    'phone': dept.phone,
                    'email': None,
                    'address': None
                })
        
        # 4. Append main Institution Email
        if obj.email:
            contacts_data.append({
                'id': 'inst-email',
                'title': 'Institution Office',
                'email': obj.email,
                'phone': None
            })
            
        return contacts_data

    def get_faculty(self, obj):
        # Fetch faculty efficiently. Avoid order_by('?') which is extremely slow on large datasets.
        # Prefetching teachers on departments is better.
        teachers = Teacher.objects.filter(department__institution=obj, is_active=True).select_related('department')[:12]
        return InstitutionPublicTeacherSerializer(teachers, many=True).data

    def get_testimonials(self, obj):
        testimonials = obj.testimonials.filter(is_active=True)
        return InstitutionTestimonialSerializer(testimonials, many=True).data

    def get_featured_admissions(self, obj):
        featured = obj.featured_admissions.filter(is_active=True)
        return InstitutionAdmissionFeaturedSerializer(featured, many=True).data
