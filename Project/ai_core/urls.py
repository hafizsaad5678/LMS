from django.urls import path
from . import views

urlpatterns = [
    # Quiz Generation
    path('quiz/init/', views.quiz_init, name='ai_quiz_init'),
    path('quiz/generate/', views.quiz_generate, name='ai_quiz_generate'),
    path('quiz/regenerate-question/', views.quiz_regenerate_question, name='ai_quiz_regenerate_question'),
    path('quiz/save/', views.quiz_save, name='ai_quiz_save'),
    
    # Student Chatbot
    path('chat/send/', views.StudentChatView.as_view(), name='ai_chat_send'),
    path('chat/sessions/', views.StudentChatSessionsView.as_view(), name='ai_chat_sessions'),
    path('chat/sessions/<uuid:session_id>/', views.StudentChatSessionsView.as_view(), name='ai_chat_session_detail'),
    path('chat/upload/', views.DocumentUploadView.as_view(), name='ai_chat_upload'),
]
