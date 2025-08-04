# agents/tasks.py
import os
from celery import shared_task
from django.conf import settings
from groq import Groq
from .models import CallRecording, ExtractedClientInfo
import json
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_call_recording_for_transcription(self, recording_id):
    """
    Celery task to handle audio transcription using Groq API.
    """
    try:
        recording = CallRecording.objects.get(id=recording_id)
        user_id = recording.uploaded_by.id if recording.uploaded_by else None

        
        recording.status = 'TRANSCRIBING'
        recording.save(update_fields=['status'])

        # Initialize Groq client
        client = Groq(api_key=settings.GROQ_API_KEY)

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

        
        recording.status = 'EXTRACTING_INFO'
        recording.save(update_fields=['status'])
        process_transcript_with_llm_agent.delay(recording.id)
        
        # ... (send status update) ...
        

    except CallRecording.DoesNotExist:
        logger.error(f"CallRecording with ID {recording_id} not found.")
        # You might send an error message to a general admin channel here
    except Exception as e:
        logger.error(f"Error transcribing CallRecording {recording_id}: {e}", exc_info=True)
        # Update status to reflect error
        recording.status = 'TRANSCRIPTION_FAILED'
        recording.save(update_fields=['status'])


@shared_task(bind=True)
def process_transcript_with_llm_agent(self, recording_id):
    """
    Celery task to extract information from the transcript using Groq LLM with MCP tools.
    """
    try:
        recording = CallRecording.objects.get(id=recording_id)
        user_id = recording.uploaded_by.id if recording.uploaded_by else None

        client = Groq(api_key=settings.GROQ_API_KEY)

        # 1. Define the tool for Groq (matching the MCP server's exposed tool)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "extract_client_info_tool",
                    "description": (
                        "Extracts key client information from a call transcript. "
                        "The tool should be called with parameters corresponding to the found information. "
                        "If a piece of information is not present, the corresponding parameter should be set to null."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            # Change all properties to be of type ['string', 'null']
                            "client_name": {"type": ["string", "null"], "description": "The full name of the potential client."},
                            "company_name": {"type": ["string", "null"], "description": "The company name of the potential client."},
                            "contact_number": {"type": ["string", "null"], "description": "The primary contact phone number of the client."},
                            "email": {"type": ["string", "null"], "description": "The primary email address of the client."},
                            "service_interest": {"type": ["string", "null"], "description": "A brief description of the services the client is interested in, derived from the conversation."},
                        },
                        "required": [], # Still good to keep this empty
                    },
                },
            }
        ]

        # 2. Craft the prompt for the LLM
        # Emphasize using the tool and focus on accuracy
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI assistant tasked with extracting structured client information from call transcripts. "
                    "Your goal is to accurately identify the client's name, company, contact details (phone, email), "
                    "their primary service interest, and any mentioned deal size estimate. "
                    "Use the `extract_client_info_tool` to format the extracted data. "
                    "IMPORTANT: If a piece of information is not explicitly mentioned, DO NOT include that parameter in the tool call. "
                    "DO NOT use placeholder values like 'N/A', 'None', or 'null'. Only return values for parameters that are directly found in the transcript."
                    "Be precise and only extract what is clearly stated or strongly implied."
                )
            },
            {
                "role": "user",
                "content": f"Here is the call transcript: '{recording.transcript_text}'\n\nPlease extract the relevant client information and call the `extract_client_info_tool`."
            }
        ]

        # 3. Call Groq with tool_choice 'auto' to allow it to decide if/when to use the tool
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192", # Or "llama3-70b-8192" if you prefer, or Groq's tool-use preview models
            tools=tools,
            tool_choice="auto", # Allow the model to decide whether to call the tool
            max_tokens=4096, # Adjust as needed
        )

        tool_calls = chat_completion.choices[0].message.tool_calls
        extracted_data = {}
        raw_llm_output = chat_completion.model_dump_json(indent=2) # Store full LLM response for debugging

        if tool_calls:
            for tool_call in tool_calls:
                if tool_call.function.name == "extract_client_info_tool":
                    extracted_args = json.loads(tool_call.function.arguments)
                    # This line is crucial: it filters out any parameters with a `None` value
                    extracted_data = {k: v for k, v in extracted_args.items() if v is not None}
                    break
        
        # Create or update ExtractedClientInfo
        extracted_info_instance, created = ExtractedClientInfo.objects.update_or_create(
            call_recording=recording,
            defaults={
                'client_name': extracted_data.get('client_name'),
                'company_name': extracted_data.get('company_name'),
                'contact_number': extracted_data.get('contact_number'),
                'email': extracted_data.get('email'),
                'service_interest': extracted_data.get('service_interest'),
                'raw_llm_output': json.loads(raw_llm_output),
                'is_approved': False,
                'approved_by': None,
                'approval_timestamp': None,
                'review_notes': None,
            }
        )
        logger.info(f"Information extracted for CallRecording {recording.id}.")

        recording.status = 'READY_FOR_REVIEW'
        recording.save(update_fields=['status'])


    except CallRecording.DoesNotExist:
        logger.error(f"CallRecording with ID {recording_id} not found for extraction.")
    except Exception as e:
        logger.error(f"Error extracting info for CallRecording {recording_id}: {e}", exc_info=True)
        recording.status = 'EXTRACTION_FAILED'
        recording.save(update_fields=['status'])