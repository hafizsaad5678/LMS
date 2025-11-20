from rest_framework import serializers
from django.contrib.auth.models import User

# -----------------------------
# ✅ Signup Serializer
# -----------------------------
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True)  # Add this


    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'username']
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # username = email
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.is_active = False
        user.save()
        return user

# -----------------------------
# ✅ Login Serializer
# -----------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

# -----------------------------
# ✅ Forgot Password Serializer
# -----------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

# -----------------------------
# ✅ Reset Password Serializer
# -----------------------------
class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
