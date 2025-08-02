# agents/serializers.py
from rest_framework import serializers
from .models import CallRecording, ExtractedClientInfo

class CallRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecording
        fields = ['id', 'uploaded_by', 'upload_timestamp', 'audio_file', 'status', 'transcript_text']
        read_only_fields = ['uploaded_by', 'upload_timestamp', 'status', 'transcript_text'] # These are set by backend

    def create(self, validated_data):
        # Automatically set uploaded_by to the current user
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
    
class ExtractedClientInfoSerializer(serializers.ModelSerializer):
    # Optional: Read-only field for related call_recording_id if needed in frontend
    call_recording_id = serializers.ReadOnlyField(source='call_recording.id')

    class Meta:
        model = ExtractedClientInfo
        fields = [
            'id', 'call_recording_id', 'client_name', 'company_name',
            'contact_number', 'email', 'service_interest',
            'is_approved', 'approved_by', 'approval_timestamp', 'review_notes',
            'raw_llm_output'
        ]
        read_only_fields = ['is_approved', 'approved_by', 'approval_timestamp'] # Onboarder updates these via custom action