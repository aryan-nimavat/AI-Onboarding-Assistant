# agents/serializers.py
from rest_framework import serializers
from .models import CallRecording

class CallRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecording
        fields = ['id', 'uploaded_by', 'upload_timestamp', 'audio_file', 'status', 'transcript_text']
        read_only_fields = ['uploaded_by', 'upload_timestamp', 'status', 'transcript_text'] # These are set by backend

    def create(self, validated_data):
        # Automatically set uploaded_by to the current user
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)