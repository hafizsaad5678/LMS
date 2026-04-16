def active_user_and_profile_rule(user):
    """Allow JWT auth only for active users with active (non-suspended) profile state."""
    if user is None or not getattr(user, 'is_active', False):
        return False

    profile_attrs = ('student_profile', 'teacher_profile', 'admin_profile')
    has_profile = False

    for attr in profile_attrs:
        profile = getattr(user, attr, None)
        if profile is None:
            continue

        has_profile = True
        if not getattr(profile, 'is_active', True):
            return False
        if getattr(profile, 'is_suspended', False):
            return False

    if has_profile:
        return True

    # Keep admin/staff users without profile able to authenticate.
    return bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
