from django.contrib import admin
from django.utils.html import format_html


class BaseAdmin(admin.ModelAdmin):
    """Base admin class for profile-based models"""
    list_display = ['get_identifier', 'full_name', 'email', 'phone', 'profile_status_display', 'is_active']
    list_filter = ['is_active', 'is_verified', 'is_suspended', 'gender', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'cnic']
    readonly_fields = ['created_at', 'updated_at', 'age_display', 'profile_status_display', 
                      'verified_at', 'suspended_at', 'last_login_at', 'edit_count', 'profile_image_display']
    list_editable = ['is_active']
    list_per_page = 20
    actions = ['activate_selected', 'deactivate_selected', 'verify_selected', 'suspend_selected']
    
    @admin.display(description='Age')
    def age_display(self, obj):
        return getattr(obj, 'age_display', 'N/A')
    
    @admin.display(description='Status')
    def profile_status_display(self, obj):
        status = getattr(obj, 'profile_status', 'Unknown')
        colors = {'Verified': 'green', 'Active': 'blue', 'Inactive': 'orange', 
                  'Suspended': 'red', 'Pending': 'gray'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          colors.get(status, 'black'), status)
    
    @admin.display(description='Profile Image')
    def profile_image_display(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;" />', 
                             obj.profile_image.url)
        return "No Image"
    
    @admin.display(description='ID')
    def get_identifier(self, obj):
        for attr in ['enrollment_number', 'employee_id', 'admin_id']:
            if hasattr(obj, attr):
                return getattr(obj, attr)
        return str(obj.id)[:8]
    
    @admin.action(description="Activate selected profiles")
    def activate_selected(self, request, queryset):
        for obj in queryset:
            obj.activate()
        self.message_user(request, f"{queryset.count()} profiles activated.")
    
    @admin.action(description="Deactivate selected profiles")
    def deactivate_selected(self, request, queryset):
        for obj in queryset:
            obj.deactivate()
        self.message_user(request, f"{queryset.count()} profiles deactivated.")

    @admin.action(description="Verify selected profiles")
    def verify_selected(self, request, queryset):
        for obj in queryset:
            obj.verify()
        self.message_user(request, f"{queryset.count()} profiles verified.")
    
    @admin.action(description="Suspend selected profiles")
    def suspend_selected(self, request, queryset):
        for obj in queryset:
            obj.suspend("Bulk suspension from admin")
        self.message_user(request, f"{queryset.count()} profiles suspended.")
