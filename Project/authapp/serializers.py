from rest_framework import serializers
from django.contrib.auth.models import User




class LoginSerializer(serializers.Serializer):
    """Serializer for login - accepts email or username"""
    username = serializers.CharField(required=True, help_text="Email or username")
    password = serializers.CharField(required=True, write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""
    password = serializers.CharField(required=True, write_only=True, min_length=6)
