from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .utils import send_verification_email, send_password_reset_email
from .config import get_verification_url
from .serializers import (
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)





class LoginThrottle(AnonRateThrottle):
    scope = 'login'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username_input = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Determine if input is email or username
        user_obj = None
        if '@' in username_input:
            user_obj = User.objects.filter(email=username_input).first()
        
        if user_obj:
            username_to_auth = user_obj.username
        else:
            username_to_auth = username_input
            
        user = authenticate(username=username_to_auth, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            # Determine User Role and get profile ID
            user_role = 'unknown'
            user_id = None
            
            # Check for superuser/staff first (highest priority)
            if user.is_superuser or user.is_staff:
                user_role = 'admin'
                if hasattr(user, 'admin_profile') and user.admin_profile is not None:
                    try:
                        user_id = str(user.admin_profile.id)
                    except (AttributeError, ValueError):
                        pass
            # Check for linked profiles
            elif hasattr(user, 'student_profile') and user.student_profile is not None:
                try:
                    user_id = str(user.student_profile.id)
                    user_role = 'student'
                except (AttributeError, ValueError):
                    pass
            elif hasattr(user, 'teacher_profile') and user.teacher_profile is not None:
                try:
                    user_id = str(user.teacher_profile.id)
                    user_role = 'teacher'
                except (AttributeError, ValueError):
                    pass
            elif hasattr(user, 'admin_profile') and user.admin_profile is not None:
                try:
                    user_id = str(user.admin_profile.id)
                    user_role = 'admin'
                except (AttributeError, ValueError):
                    pass
            
            response_data = {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user_role,
                "username": user.username,
                "email": user.email,
                "full_name": user.get_full_name(),
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser
            }
            
            if user_id:
                response_data["user_id"] = user_id
                if user_role == 'student':
                    response_data["student_id"] = user_id
                elif user_role == 'teacher':
                    response_data["teacher_id"] = user_id
                elif user_role == 'admin':
                    response_data["admin_id"] = user_id
            
            return Response(response_data)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        generic_response = {
            "message": "If an account with this email exists, a password reset link has been sent."
        }
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(generic_response)
        
        token = default_token_generator.make_token(user)
        try:
            send_password_reset_email(user, token, user.pk)
        except Exception:
            return Response({"error": "Unable to send reset email at the moment. Please try again shortly."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(generic_response)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uid, token):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "Password has been reset successfully!"})
        return Response({"error": "Invalid or expired link"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
