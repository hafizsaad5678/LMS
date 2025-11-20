from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .utils import send_verification_email, send_password_reset_email
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)

# -----------------------------
# ✅ Signup
# -----------------------------
@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_verification_email(user, token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_link = f"http://127.0.0.1:8000/api/verify/{uid}/{token}/"
        return JsonResponse({
            "message": "Signup successful! Check your email to verify account.",
            "verify_link": verify_link
        })
    return JsonResponse(serializer.errors, status=400)

# -----------------------------
# ✅ Email Verification
# -----------------------------
@api_view(['GET'])
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return JsonResponse({"error": "Invalid link"}, status=400)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return JsonResponse({"message": "✅ Email verified successfully!"})
    return JsonResponse({"error": "❌ Invalid or expired verification link."}, status=400)

# -----------------------------
# ✅ Login
# -----------------------------
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            # Get user role from profile
            user_role = 'student'  # default
            if hasattr(user, 'profile'):
                user_role = user.profile.role
            
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user_role,
                "username": user.username
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# ✅ Forgot Password
# -----------------------------
@api_view(['POST'])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email does not exist"}, status=404)
        
        print("UID in forgot password view:", user.pk) 
        token = default_token_generator.make_token(user)
        send_password_reset_email(user, token , user.pk)  

        return JsonResponse({"message": "✅ Password reset email sent!", "uid": user.pk, "token": token})
    return JsonResponse(serializer.errors, status=400)

# -----------------------------
# ✅ Reset Password
# -----------------------------
@api_view(['POST'])
def reset_password(request, uid, token):
    print(request.data,uid,token)
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(pk=uid)
        except Exception:
            return JsonResponse({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return JsonResponse({"message": "✅ Password has been reset successfully!"})
        return JsonResponse({"error": "❌ Invalid or expired link"}, status=400)
    return JsonResponse(serializer.errors, status=400)
