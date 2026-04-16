from rest_framework import serializers
from ..models import Material, Announcement, ActivityLog


ALLOWED_MATERIAL_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.zip',
    '.mp4', '.avi', '.jpg', '.jpeg', '.png'
}
MAX_MATERIAL_FILE_SIZE = 50 * 1024 * 1024


class MaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = Material
        fields = '__all__'

    def validate(self, attrs):
        title = str(attrs.get('title', '')).strip()
        if not title:
            raise serializers.ValidationError({'title': 'This field is required.'})

        if attrs.get('subject') is None:
            raise serializers.ValidationError({'subject': 'This field is required.'})

        file_upload = attrs.get('file_upload')
        if self.instance is None and file_upload is None:
            raise serializers.ValidationError({'file_upload': 'A file is required.'})

        if file_upload is not None:
            filename = (getattr(file_upload, 'name', '') or '').lower()
            if not any(filename.endswith(ext) for ext in ALLOWED_MATERIAL_EXTENSIONS):
                raise serializers.ValidationError({'file_upload': 'Unsupported file type.'})

            if getattr(file_upload, 'size', 0) > MAX_MATERIAL_FILE_SIZE:
                raise serializers.ValidationError({'file_upload': 'File size exceeds 50MB limit.'})

        return attrs


class AnnouncementSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'