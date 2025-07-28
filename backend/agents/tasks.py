# agents/tasks.py
import os
from celery import shared_task
from django.conf import settings
from groq import Groq
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CallRecording
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_call_recording_for_transcription(self, recording_id):
    """
    Celery task to handle audio transcription using Groq API.
    """
    channel_layer = get_channel_layer()
    try:
        recording = CallRecording.objects.get(id=recording_id)
        user_id = recording.uploaded_by.id if recording.uploaded_by else None

        # Notify frontend: Status Update - Transcribing
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_message",
                "message": {
                    "type": "call_status",
                    "call_id": recording.id,
                    "status": "TRANSCRIBING",
                    "detail": "Sending audio to Groq for transcription."
                }
            }
        )
        recording.status = 'TRANSCRIBING'
        recording.save(update_fields=['status'])

        # Initialize Groq client
        client = Groq(api_key=settings.GROQ_API_KEY) # Use env variable for production

        # Open audio file in binary read mode
        audio_file_path = recording.audio_file.path
        with open(audio_file_path, "rb") as file:
            transcript = client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), file.read()),
                model="whisper-large-v3", # Groq's STT model
            )

        recording.transcript_text = transcript.text
        recording.status = 'TRANSCRIBED'
        recording.save(update_fields=['transcript_text', 'status'])
        logger.info(f"CallRecording {recording.id} successfully transcribed.")

        # Notify frontend: Status Update - Transcribed
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_message",
                "message": {
                    "type": "call_status",
                    "call_id": recording.id,
                    "status": "TRANSCRIBED",
                    "detail": "Transcription complete. Ready for NLP processing."
                }
            }
        )

        # TODO: Trigger next phase task here (NLP extraction in Week 3)
        # from .tasks import process_transcript_with_llm_agent
        # process_transcript_with_llm_agent.delay(recording.id)

    except CallRecording.DoesNotExist:
        logger.error(f"CallRecording with ID {recording_id} not found.")
        # You might send an error message to a general admin channel here
    except Exception as e:
        logger.error(f"Error transcribing CallRecording {recording_id}: {e}", exc_info=True)
        # Update status to reflect error
        recording.status = 'TRANSCRIPTION_FAILED'
        recording.save(update_fields=['status'])
        # Notify frontend: Status Update - Failed
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_message",
                "message": {
                    "type": "call_status",
                    "call_id": recording.id,
                    "status": "TRANSCRIPTION_FAILED",
                    "detail": f"Transcription failed: {str(e)}"
                }
            }
        )