from django.db import models
from django.contrib.auth.models import User

class CallRecording(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='call_recordings/') # Will store files in MEDIA_ROOT/call_recordings/
    status = models.CharField(max_length=50, default='UPLOADED') # e.g., UPLOADED, TRANSCRIBING, TRANSCRIBED, EXTRACTING, READY_FOR_REVIEW, APPROVED, REJECTED
    transcript_text = models.TextField(blank=True, null=True) # To store the STT output

    def __str__(self):
        return f"Call {self.id} by {self.uploaded_by.username if self.uploaded_by else 'Unknown'} - {self.status}"