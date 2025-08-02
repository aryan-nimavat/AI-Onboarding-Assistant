from django.contrib import admin
from .models import CallRecording, ExtractedClientInfo, Client

# Register your models here.
admin.site.register(CallRecording)
admin.site.register(ExtractedClientInfo)
admin.site.register(Client)