from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsTeacherUser(permissions.BasePermission):
    """Allows access only to teacher users."""
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'teacher_profile'))


class IsStudentUser(permissions.BasePermission):
    """Allows access only to student users."""
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'student_profile'))


class IsProfileOwner(permissions.BasePermission):
    """Allows users to access only their own profile."""
    def has_object_permission(self, request, view, obj):
        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class ReadOnlyForStudents(permissions.BasePermission):
    """Allows read-only access for students, full access for teachers/admins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations only for teachers/admins
        return bool(
            request.user and 
            (request.user.is_staff or hasattr(request.user, 'teacher_profile'))
        )


class CanGradeAssignments(permissions.BasePermission):
    """Allows only teachers to grade assignments."""
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return bool(request.user and hasattr(request.user, 'teacher_profile'))
        return True


class CanMarkAttendance(permissions.BasePermission):
    """Allows only teachers to mark attendance."""
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return bool(request.user and hasattr(request.user, 'teacher_profile'))
        return True