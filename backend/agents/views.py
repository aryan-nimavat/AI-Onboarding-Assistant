# agents/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CallRecording, ExtractedClientInfo, Client
from .serializers import CallRecordingSerializer
from .tasks import process_call_recording_for_transcription # celery task
from .serializers import ExtractedClientInfoSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db import models
import logging

logger = logging.getLogger(__name__)


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
    


class ExtractedClientInfoViewSet(viewsets.ModelViewSet):
    # Only show unapproved or approved by current user, or all for superuser
    queryset = ExtractedClientInfo.objects.all().order_by('-call_recording__upload_timestamp')
    serializer_class = ExtractedClientInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ExtractedClientInfo.objects.all().order_by('-call_recording__upload_timestamp')
        # Onboarders see records ready for review or those they have already approved/rejected
        return ExtractedClientInfo.objects.filter(
            models.Q(call_recording__status='READY_FOR_REVIEW') |
            models.Q(approved_by=self.request.user)
        ).order_by('-call_recording__upload_timestamp')

    # Custom action for approving extracted data
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        try:
            extracted_info = self.get_object()

            # Ensure it's not already approved/rejected
            if extracted_info.is_approved:
                return Response({"detail": "This record is already approved."}, status=status.HTTP_400_BAD_REQUEST)
            if extracted_info.call_recording.status == 'REJECTED':
                    return Response({"detail": "This record has been rejected."}, status=status.HTTP_400_BAD_REQUEST)


            # Update ExtractedClientInfo fields based on request body (for corrections)
            serializer = self.get_serializer(extracted_info, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            # Save the potentially corrected data
            extracted_info = serializer.save(
                is_approved=True,
                approved_by=request.user,
                approval_timestamp=timezone.now(),
                review_notes=request.data.get('review_notes', extracted_info.review_notes)
            )

            # Create a new Client record
            client_record = Client.objects.create(
                name=extracted_info.client_name,
                company=extracted_info.company_name,
                contact_number=extracted_info.contact_number,
                email=extracted_info.email,
                service_purchased=extracted_info.service_interest,
                original_extraction=extracted_info
            )

            # Update the parent CallRecording status
            extracted_info.call_recording.status = 'APPROVED'
            extracted_info.call_recording.save(update_fields=['status'])

            # Notify frontend of approval
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}", # Notify the user who approved
                {
                    "type": "send_message",
                    "message": {
                        "type": "client_approved",
                        "call_id": extracted_info.call_recording.id,
                        "client_id": client_record.id,
                        "status": "APPROVED",
                        "detail": f"Client '{client_record.name}' approved and saved."
                    }
                }
            )
            # Optional: Notify a general admin channel or all users on a dashboard that a client was approved
            # async_to_sync(channel_layer.group_send)(
            #     "all_onboarders",
            #     { "type": "send_message", "message": { ... }}
            # )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ExtractedClientInfo.DoesNotExist:
            return Response({"detail": "Extracted info not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error approving extracted info {pk}: {e}", exc_info=True)
            # Consider setting status of call_recording or extraction to a problematic state
            return Response({"detail": f"An error occurred during approval: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Custom action for rejecting extracted data (meaning it needs manual re-entry)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        try:
            extracted_info = self.get_object()

            if extracted_info.is_approved or extracted_info.call_recording.status == 'REJECTED':
                return Response({"detail": "This record is already processed."}, status=status.HTTP_400_BAD_REQUEST)

            extracted_info.is_approved = False
            extracted_info.approved_by = request.user
            extracted_info.approval_timestamp = timezone.now()
            extracted_info.review_notes = request.data.get('review_notes', 'Rejected by user.') # Mandate review notes for rejection?
            extracted_info.save(update_fields=['is_approved', 'approved_by', 'approval_timestamp', 'review_notes'])

            extracted_info.call_recording.status = 'REJECTED' # Mark parent call as rejected
            extracted_info.call_recording.save(update_fields=['status'])

            # Notify frontend of rejection
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",
                {
                    "type": "send_message",
                    "message": {
                        "type": "client_rejected",
                        "call_id": extracted_info.call_recording.id,
                        "status": "REJECTED",
                        "detail": "Information rejected. Manual action required."
                    }
                }
            )

            return Response({"status": "Extracted information rejected."}, status=status.HTTP_200_OK)

        except ExtractedClientInfo.DoesNotExist:
            return Response({"detail": "Extracted info not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting extracted info {pk}: {e}", exc_info=True)
            return Response({"detail": f"An error occurred during rejection: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)