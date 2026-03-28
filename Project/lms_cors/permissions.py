from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users (staff or admin_profile)."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or hasattr(request.user, 'admin_profile')


class IsTeacherUser(permissions.BasePermission):
    """Allows access only to teacher users."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'teacher_profile')


class IsStudentUser(permissions.BasePermission):
    """Allows access only to student users."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'student_profile')


class IsAdminOrTeacher(permissions.BasePermission):
    """Allows access to admin or teacher users."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or 
            hasattr(request.user, 'admin_profile') or 
            hasattr(request.user, 'teacher_profile')
        )


class IsProfileOwner(permissions.BasePermission):
    """Allows users to access only their own profile."""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsProfileOwnerOrAdmin(permissions.BasePermission):
    """Allows profile owner or admin to access."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or hasattr(request.user, 'admin_profile'):
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class ReadOnlyForStudents(permissions.BasePermission):
    """Read-only for students, full access for teachers/admins."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Safe methods (GET, HEAD, OPTIONS) allowed for all authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations only for teachers/admins
        return (
            request.user.is_staff or 
            hasattr(request.user, 'admin_profile') or 
            hasattr(request.user, 'teacher_profile')
        )


class AdminFullAccess(permissions.BasePermission):
    """Full CRUD for admin, read-only for others."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff or hasattr(request.user, 'admin_profile')


class CanManageStudents(permissions.BasePermission):
    """Admin can do everything, Teacher can view, Student can view own."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin - full access
        if request.user.is_staff or hasattr(request.user, 'admin_profile'):
            return True
        
        # Teacher - read only
        if hasattr(request.user, 'teacher_profile'):
            return request.method in permissions.SAFE_METHODS
        
        # Student - handled at object level
        if hasattr(request.user, 'student_profile'):
            return request.method in permissions.SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin - full access
        if request.user.is_staff or hasattr(request.user, 'admin_profile'):
            return True
        
        # Student can only view their own profile
        if hasattr(request.user, 'student_profile'):
            if hasattr(obj, 'user'):
                return obj.user == request.user
        
        # Teacher can view all students
        if hasattr(request.user, 'teacher_profile'):
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsTeacherOrAdminForWrite(permissions.BasePermission):
    """
    Teachers and admins can write, everyone authenticated can read.
    Used for grading assignments and marking attendance.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (
            hasattr(request.user, 'teacher_profile') or 
            request.user.is_staff or 
            hasattr(request.user, 'admin_profile')
        )


# Aliases for backward compatibility
CanGradeAssignments = IsTeacherOrAdminForWrite
CanMarkAttendance = IsTeacherOrAdminForWrite


class CanSubmitAssignment(permissions.BasePermission):
    """Students can submit, teachers/admin can view all."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Everyone can view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only students can submit (POST)
        if request.method == 'POST':
            return hasattr(request.user, 'student_profile')
        
        # Admin/Teacher can update/delete
        return (
            request.user.is_staff or 
            hasattr(request.user, 'admin_profile') or 
            hasattr(request.user, 'teacher_profile')
        )
