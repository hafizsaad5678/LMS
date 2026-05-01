import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/' + os.environ.get('ADMIN_URL', 'admin/')), name='root_redirect'),
    path(os.environ.get('ADMIN_URL', 'admin/'), admin.site.urls),
    path('api/', include('authapp.urls')),
    path('api/', include('lms_cors.urls')),
    path('api/institution/', include('institution_profile.urls')),
    path('api/ai/', include('ai_core.urls')),
]

# Serve media files (in production, Nginx/Apache should handle this directly)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
