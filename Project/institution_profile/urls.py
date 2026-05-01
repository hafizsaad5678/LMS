from django.urls import path
from .views import institution_profile_view, public_admission_inquiry

urlpatterns = [
    path('inquiry/', public_admission_inquiry, name='public-admission-inquiry'),
    path('<slug:slug>/', institution_profile_view, name='institution-profile'),
]
