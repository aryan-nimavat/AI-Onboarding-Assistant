# generate_audio.py
from gtts import gTTS
import os

scripts = {
    "script_1_complete_info": """
        Hello, this is Alex from Solv Solutions. I'm calling to follow up on your recent inquiry about our onboarding services. Am I speaking with Jane Foster?
        Hi Alex, yes, this is Jane. I'm the project manager over at Tech Innovators. Your website mentioned a package that integrates with our existing CRM, and I'd like to get more information on that. I can be reached at (987) 654-3210, and my email is jane.foster@techinnovators.com.
        That's great. So your primary interest is in our CRM integration package for Tech Innovators. I'll get you some details right away.
    """,
    "script_2_missing_contact_number": """
        Good morning, this is Michael. I'm calling about the corporate training services you expressed interest in. Who am I speaking with?
        Hello Michael, this is Robert Downey from Aero Corp. We're looking for a service that focuses on leadership training and team building. I have a very busy schedule, so if you could just email me the full brochure, that would be perfect. My email is robert.d@aerocorp.com.
        Okay, Robert, I'll send that brochure to you right away at that email address. Is there anything else I can help you with today?
    """,
    "script_3_freelancer": """
        Hi, I'm calling about our digital marketing solutions. Is this Sarah Connor?
        Yes, hi. I'm a freelance consultant, so I don't have a company name, but I'm definitely interested in your social media advertising services. My email is sarah.c@gmail.com. You can reach me on my personal phone at (555) 123-4567.
        Alright, Sarah. I'll send you some information about our services. Thank you for your time.
    """,
    "script_4_minimal_details": """
        Hello, this is Chris from our support team. Can I get your name and the issue you're having?
        Hi, this is Mark. I'm calling to inquire about your new web hosting plan. My phone number is 999-888-7777. My email is mark.s@email.com.
        Okay, Mark, I can help you with that. I'll get some information for you.
    """,
    "script_5_irrelevant": """
        Hello, you've reached our support line. How can I help you today?
        Hi, I'm just calling to let you know that one of your drivers, a guy named Tom, left his lights on and I just wanted to pass that along to him. Could you tell me if he's working on a delivery in the downtown area today?
        Thank you for letting us know. I'll pass that message along.
    """
}

# Create the directory if it doesn't exist
output_dir = "test_audio"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for name, text in scripts.items():
    print(f"Generating audio for {name}...")
    tts = gTTS(text, lang='en')
    file_path = os.path.join(output_dir, f"{name}.mp3")
    tts.save(file_path)
    print(f"Saved to {file_path}")

print("\nAll audio files generated successfully.")