from django.urls import path
from .views import signup , login, verify_email, forgot_password, reset_password
urlpatterns = [
    path('signup/', signup, name='signup'), 
    path('login/', login, name='login'),
    # path('send-basic-email/', send_basic_email, name='send_basic_email'),
    # path('send-advanced-email/', send_advanced_email, name='send_advanced_email'),
    path('verify/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('forgot-password/',forgot_password ,name='forgot_password'),
    path('reset-password/<uid>/<token>/', reset_password, name='reset_password'),

    
]