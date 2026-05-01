from django.db import models
import uuid

class Institution(models.Model):
    """
    Institution model - The top-level entity representing a college/university.
    All departments belong to an institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300, help_text="Full name of the institution")
    short_name = models.CharField(max_length=50, blank=True, help_text="Abbreviation e.g., MIT, NUST")
    code = models.CharField(max_length=20, unique=True, help_text="Unique institution code")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    # Address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Pakistan')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional Info
    established_year = models.IntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='institution_covers/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mission = models.TextField(blank=True, null=True, help_text='Institution mission statement')
    vision = models.TextField(blank=True, null=True, help_text='Institution vision statement')
    
    # Principal Info
    principal_name = models.CharField(max_length=200, blank=True, null=True)
    principal_image = models.ImageField(upload_to='institution_principal/', blank=True, null=True)
    principal_message = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, help_text='URL identifier e.g. gc-aroop')
    theme_color = models.CharField(max_length=7, default='#3b82f6', help_text='HEX brand color')
    secondary_color = models.CharField(max_length=7, default='#1e293b', help_text='HEX secondary brand color')
    tagline = models.CharField(max_length=300, blank=True, null=True, help_text='Short slogan e.g. "Excellence in Education"')
    footer_text = models.TextField(blank=True, null=True, help_text='Custom footer text')
    
    # Social Links
    facebook_url = models.URLField(max_length=300, blank=True, null=True)
    twitter_url = models.URLField(max_length=300, blank=True, null=True)
    linkedin_url = models.URLField(max_length=300, blank=True, null=True)
    instagram_url = models.URLField(max_length=300, blank=True, null=True)
    youtube_url = models.URLField(max_length=300, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'institutions'
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class InstitutionGallery(models.Model):
    """Gallery images for institution profile pages."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='institution_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        db_table = 'institution_gallery'
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        label = self.caption or 'Image'
        return f"{self.institution.name} - {label}"


class InstitutionFeature(models.Model):
    """Reusable highlight cards for an institution profile."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='features'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text='Optional icon class e.g. bi bi-stars')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']
        db_table = 'institution_features'
        verbose_name = 'Institution Feature'
        verbose_name_plural = 'Institution Features'

    def __str__(self):
        return f"{self.title} - {self.institution.name}"


class InstitutionTestimonial(models.Model):
    """Student/Alumni testimonials for the institution public profile."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='testimonials'
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="e.g. 'Alumni, Class of 2020' or 'Computer Science Student'")
    content = models.TextField()
    profile_image = models.ImageField(upload_to='institution_testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, help_text="1 to 5 stars")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institution_testimonials'
        ordering = ['order', '-created_at']
        verbose_name = 'Institution Testimonial'
        verbose_name_plural = 'Institution Testimonials'

    def __str__(self):
        return f"{self.name} - {self.institution.name}"


class InstitutionEvent(models.Model):
    """Public-facing events tied to an institution."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='events'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'event_date', 'title']
        db_table = 'institution_events'
        verbose_name = 'Institution Event'
        verbose_name_plural = 'Institution Events'

    def __str__(self):
        return f"{self.institution.name} - {self.title}"


class InstitutionAdmissionInfo(models.Model):
    """Simple admissions/sessions info section for an institution."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='admissions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    apply_url = models.URLField(blank=True, null=True, help_text='Single admissions application link for this institution')
    apply_email = models.EmailField(blank=True, null=True, help_text='Admissions contact email (optional)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        db_table = 'institution_admissions'
        verbose_name = 'Admissions Info'
        verbose_name_plural = 'Admissions Info'

    def __str__(self):
        return f"{self.institution.name} - {self.title}"


class InstitutionContact(models.Model):
    """Optional contact blocks for an institution profile."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'order', 'created_at']
        db_table = 'institution_contacts'
        verbose_name = 'Institution Contact'
        verbose_name_plural = 'Institution Contacts'

    def __str__(self):
        label = self.title or 'Contact'
        return f"{self.institution.name} - {label}"
