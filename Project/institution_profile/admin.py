from django.contrib import admin
from .models import (
    Institution, InstitutionGallery, InstitutionFeature, InstitutionEvent,
    InstitutionAdmissionInfo, InstitutionContact
)

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'code', 'city', 'country', 'department_count', 'is_active']
    list_filter = ['is_active', 'country', 'city', 'established_year']
    search_fields = ['name', 'short_name', 'code', 'email', 'city']
    list_editable = ['is_active']
    list_per_page = 20
    
    @admin.display(description='Departments')
    def department_count(self, obj):
        return obj.departments.count()


@admin.register(InstitutionGallery)
class InstitutionGalleryAdmin(admin.ModelAdmin):
    list_display = ['institution', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['institution', 'is_featured']
    search_fields = ['caption', 'institution__name']
    list_editable = ['is_featured', 'order']
    list_per_page = 20


@admin.register(InstitutionFeature)
class InstitutionFeatureAdmin(admin.ModelAdmin):
    list_display = ['institution', 'title', 'icon', 'is_active', 'order']
    list_filter = ['institution', 'is_active']
    search_fields = ['title', 'description', 'institution__name']
    list_editable = ['is_active', 'order']
    list_per_page = 20


@admin.register(InstitutionEvent)
class InstitutionEventAdmin(admin.ModelAdmin):
    list_display = ['institution', 'title', 'event_date', 'location', 'is_active', 'order']
    list_filter = ['institution', 'is_active', 'event_date']
    search_fields = ['title', 'description', 'location', 'institution__name']
    list_editable = ['is_active', 'order']
    list_per_page = 20


@admin.register(InstitutionAdmissionInfo)
class InstitutionAdmissionInfoAdmin(admin.ModelAdmin):
    list_display = ['institution', 'title', 'apply_url', 'apply_email', 'is_active', 'updated_at']
    list_filter = ['institution', 'is_active']
    search_fields = ['title', 'description', 'apply_email', 'institution__name']
    list_editable = ['is_active']
    list_per_page = 20


@admin.register(InstitutionContact)
class InstitutionContactAdmin(admin.ModelAdmin):
    list_display = ['institution', 'title', 'email', 'phone', 'is_primary', 'order']
    list_filter = ['institution', 'is_primary']
    search_fields = ['title', 'email', 'phone', 'institution__name']
    list_editable = ['is_primary', 'order']
    list_per_page = 20
