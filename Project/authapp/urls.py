from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import login, forgot_password, reset_password

urlpatterns = [
    path('login/', login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/',forgot_password ,name='forgot_password'),
    path('reset-password/<uid>/<token>/', reset_password, name='reset_password'),
]

    # path('send-basic-email/', send_basic_email, name='send_basic_email'),
        # path('send-advanced-email/', send_advanced_email, name='send_advanced_email'),