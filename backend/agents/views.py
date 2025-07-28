# agents/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CallRecording
from .serializers import CallRecordingSerializer
from .tasks import process_call_recording_for_transcription # celery task

class CallRecordingViewSet(viewsets.ModelViewSet):
    queryset = CallRecording.objects.all().order_by('-upload_timestamp')
    serializer_class = CallRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the user who uploads is set
        recording = serializer.save(uploaded_by=self.request.user, status='UPLOADED')
        # Trigger the Celery task after saving the record
        process_call_recording_for_transcription.delay(recording.id)

    # Optional: Custom action to re-process if needed
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reprocess_transcription(self, request, pk=None):
        try:
            recording = self.get_object()
            recording.status = 'REPROCESSING_TRANSCRIPTION'
            recording.save(update_fields=['status'])
            process_call_recording_for_transcription.delay(recording.id)
            return Response({'status': 'Transcription reprocessing initiated'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Filter recordings by current user
    def get_queryset(self):
        if self.request.user.is_superuser: # Admins can see all
            return CallRecording.objects.all().order_by('-upload_timestamp')
        return CallRecording.objects.filter(uploaded_by=self.request.user).order_by('-upload_timestamp')