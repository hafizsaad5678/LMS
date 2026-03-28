# authapp/config.py
from django.conf import settings

# URL Configuration - Override these in settings.py for production
BACKEND_URL = getattr(settings, 'BACKEND_URL', 'http://127.0.0.1:8000')
FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

def get_verification_url(uid, token):
    """Generate email verification URL"""
    return f"{BACKEND_URL}/api/verify/{uid}/{token}/"

def get_password_reset_url(uid, token):
    """Generate password reset URL (points to frontend)"""
    return f"{FRONTEND_URL}/reset-password/{uid}/{token}/"
