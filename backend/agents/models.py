from django.db import models
from django.contrib.auth.models import User

class CallRecording(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='call_recordings/') # Will store files in MEDIA_ROOT/call_recordings/
    status = models.CharField(
        max_length=50,
        default='UPLOADED',
        choices=[
            ('UPLOADED', 'Uploaded'),
            ('TRANSCRIBING', 'Transcribing'),
            ('TRANSCRIBED', 'Transcribed'),
            ('EXTRACTING_INFO', 'Extracting Information'), # New status
            ('READY_FOR_REVIEW', 'Ready for Review'), # New status
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('TRANSCRIPTION_FAILED', 'Transcription Failed'),
            ('EXTRACTION_FAILED', 'Information Extraction Failed'), # New status
        ]
    )
    transcript_text = models.TextField(blank=True, null=True) # To store the STT output

    def __str__(self):
        return f"Call {self.id} by {self.uploaded_by.username if self.uploaded_by else 'Unknown'} - {self.status}"
    
class ExtractedClientInfo(models.Model):
    call_recording = models.OneToOneField(CallRecording, on_delete=models.CASCADE, related_name='extracted_info')
    client_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    service_interest = models.TextField(blank=True, null=True)

    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_extractions')
    approval_timestamp = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    raw_llm_output = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Extracted Info for Call {self.call_recording.id} - Approved: {self.is_approved}"

class Client(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    service_purchased = models.TextField(blank=True, null=True)
    onboard_date = models.DateField(auto_now_add=True)
    original_extraction = models.OneToOneField(ExtractedClientInfo, on_delete=models.SET_NULL, null=True, blank=True, related_name='final_client_record')

    def __str__(self):
        return self.name