from django.db import models
import uuid
import logging
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import secrets
import string
from authapp.utils import send_welcome_email

logger = logging.getLogger(__name__)


def validate_profile_image_size(value):
    """Validate image size (max 5MB)"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    return value


def profile_image_path(instance, filename):
    """Generate path for profile images: profiles/<model_name>/<id>/filename"""
    model_name = instance.__class__.__name__.lower()
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profiles', model_name, str(instance.id), filename)


class BaseProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-'),
        ('unknown', 'Unknown')
    ]
    
    # Core Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='%(class)s_profile'
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='prefer_not_to_say')
    
    # Additional Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='unknown')
    nationality = models.CharField(max_length=50, default='Pakistani')
    cnic = models.CharField(max_length=15, blank=True, null=True, unique=True)
    
    # Contact Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Profile Media
    profile_image = models.ImageField(
        upload_to=profile_image_path,
        blank=True,
        null=True,
        validators=[validate_profile_image_size]
    )
    
    # Status Flags
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    edit_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    
    def clean(self):
        """Custom validation"""
        if self.date_of_birth:
            if self.date_of_birth > timezone.now().date():
                raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future'})
        
        # CNIC validation - strip dashes and check length
        if self.cnic:
            cnic_digits = self.cnic.replace('-', '').replace(' ', '')
            if len(cnic_digits) != 13 or not cnic_digits.isdigit():
                raise ValidationError({'cnic': 'CNIC must be exactly 13 digits (with or without dashes)'})
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age
    
    @property
    def age_display(self):
        """Formatted age display"""
        age = self.age
        if age is None:
            return "N/A"
        return f"{age} years"
    
    @property
    def profile_status(self):
        """Get profile status"""
        if self.is_suspended:
            return "Suspended"
        elif not self.is_active:
            return "Inactive"
        elif self.is_verified:
            return "Verified"
        else:
            return "Pending"
    
    def create_user_account(self, password=None):
        """
        Create or link a Django User account.
        Uses update() to avoid triggering save() and potential infinite recursion.
        Returns: (user_created, user)
        """
        if self.user:
            return False, self.user  # Already linked
        
        if not self.email:
            return False, None
        
        try:
            # Check if user with this email already exists
            existing_user = User.objects.filter(email=self.email).first()
            if existing_user:
                # Generate a new random password for the existing user
                temp_password = ''.join(secrets.choice(string.digits) for _ in range(16))
                existing_user.set_password(temp_password)
                existing_user.save()
                
                # Link and Update
                self.__class__.objects.filter(pk=self.pk).update(user=existing_user)
                self.user = existing_user
                
                # Send email to the existing user
                try:
                    send_welcome_email(existing_user, temp_password)
                except Exception as e:
                    logger.error("Failed to send welcome email to existing user: %s", e)
                
                return False, existing_user
            
            # Generate username from email
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user with temporary password
            if not password:
                # Generate random secure password (16 numeric characters)
                password = ''.join(secrets.choice(string.digits) for _ in range(16))
                
            user = User.objects.create_user(
                username=username,
                email=self.email,
                password=password,
                first_name=self.full_name.split(' ')[0] if ' ' in self.full_name else self.full_name,
                last_name=' '.join(self.full_name.split(' ')[1:]) if ' ' in self.full_name else '',
                is_active=True # Force active for new accounts
            )
            
            # Link the user to this profile instance
            self.user = user
            
            # If the profile already exists in DB, update it immediately
            if self.pk:
                self.__class__.objects.filter(pk=self.pk).update(user=user)
            
            # Send Welcome Email
            try:
                send_welcome_email(user, password)
            except Exception as e:
                logger.error("Failed to send welcome email: %s", e)
            
            return True, user
            
        except Exception as e:
            # Log error instead of print in production
            return False, None
    
    def reset_password(self, new_password):
        """Reset user password"""
        if self.user:
            self.user.set_password(new_password)
            self.user.save()
            return True
        return False
    
    def activate(self):
        """Activate the profile"""
        self.is_active = True
        self.is_suspended = False
        if self.user:
            self.user.is_active = True
            self.user.save()
        self.save()
    
    def deactivate(self):
        """Deactivate the profile"""
        self.is_active = False
        if self.user:
            self.user.is_active = False
            self.user.save()
        self.save()
    
    def suspend(self, reason=""):
        """Suspend the profile"""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        if self.user:
            self.user.is_active = False
            self.user.save()
        
        if reason:
            self.notes = f"{self.notes}\nSuspended on {self.suspended_at}: {reason}" if self.notes else f"Suspended on {self.suspended_at}: {reason}"
        
        self.save()
    
    def verify(self):
        """Verify the profile"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
    
    def record_login(self):
        """Record last login time"""
        self.last_login_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to add validation"""
        self.full_clean()
        
        # Increment edit count on updates
        if self.pk:
            self.edit_count += 1
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Ensure associated user is deleted when profile is deleted"""
        user = self.user
        super().delete(*args, **kwargs)
        if user:
            user.delete()
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
