# chatbot.py - Main chatbot logic
import os
import sys
import json
import time
import itertools
import threading
import search
import memory
import book_downloader
import book_analysis
import fetch_google
from google.cloud import texttospeech  # ✅ Google Cloud TTS
from openai import OpenAI
from speech import Speech  # Importing speech module

# ✅ Set Google Application Credentials explicitly in the script
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\shaza\.lmstudio\Oynx_Ai\ai-voice-449905-45464ad2e6bb.json"

# Define Assistant Name
ASSISTANT_NAME = "OYNX"

# Initialize LM Studio Client
client = OpenAI(base_url="http://127.0.0.1:1234/V1", api_key="lm-studio")
MODEL = "deepseek-r1-distill-qwen-7b"  # Upgraded to a more advanced model

# === Spinner Class (For Thinking Animation) ===
class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = False
        self.delay = 0.03
        self.message = message
        self.thread = None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def _spin(self):
        while self.busy:
            self.write(f"\r{self.message} {next(self.spinner)}")
            time.sleep(self.delay)
        self.write("\r\033[K")

    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        self.write("\r")

# === Smart User Setup ===
def setup_user():
    """Initializes user profile and settings."""
    print(f"\n🎩 Welcome! I am {ASSISTANT_NAME}, your personal butler. Preparing your settings...")
    user_name = input("\n💡 How shall I address you? ").strip()
    profile = memory.get_user_profile(user_name)
    
    default_preferences = {
        "personality": "Butler",
        "speech_enabled": False,
        "search_enabled": True,
        "ai_response_enabled": True
    }
    
    user_preferences = {**default_preferences, **(profile or {})}
    if not profile:
        memory.create_user_profile(user_name)
        memory.update_user_preference(user_name, "preferences", json.dumps(user_preferences))
    
    voice_preference = input("\n🎤 Would you like OYNX to speak? (yes/no): ").strip().lower()
    user_preferences["speech_enabled"] = voice_preference == "yes"
    
    print(f"\n✅ Setup complete! Welcome, {user_name}.")
    return user_name, user_preferences

# === AI Bot Logic ===
def generate_ai_response(user_input, conversation_history, user_preferences):
    """Generates AI responses and speaks if enabled."""
    stored_knowledge = memory.get_from_memory(user_input) or None

    messages = [
        {"role": "system", "content": "You are OYNX, a sophisticated AI butler with deep knowledge and a calm, authoritative tone."}
    ]

    if stored_knowledge:
        messages.append({"role": "user", "content": f"Relevant stored knowledge: {stored_knowledge}"})

    for user_msg, bot_msg in conversation_history[-5:]:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": user_input})

    with Spinner(f"{ASSISTANT_NAME} is processing your request..."):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

    ai_response = response.choices[0].message.content.strip("</think>")  # Remove unwanted XML tags

    # ✅ If AI doesn't know, fallback to search
    if "I am not sure" in ai_response or "I do not know" in ai_response:
        with Spinner(f"{ASSISTANT_NAME} is searching the internet..."):
            search_results = fetch_google.fetch_google_content(user_input)
            if search_results["status"] == "success":
                ai_response += "\n\n" + search_results["formatted_results"]
    
    # ✅ Store response in memory for future context
    memory.save_to_memory(user_input, ai_response)

    print(f"\n{ASSISTANT_NAME}: {ai_response}")

    if user_preferences["speech_enabled"]:
        Speech.speak(ai_response)  # Deeper, more authoritative voice

    return ai_response

# === Chatbot Loop ===
def chat_loop():
    """Main chatbot loop with voice control."""
    user_name, user_preferences = setup_user()
    conversation_history = []

    print(f"\n✅ Voice Mode {'Enabled' if user_preferences['speech_enabled'] else 'Disabled'}. I await your instructions.")

    while True:
        if user_preferences["speech_enabled"]:
            user_input = Speech.listen()
            if not user_input:
                continue
        else:
            user_input = input("\n📝 You: ").strip()
            if not user_input:
                continue

        if user_input.lower() in ["quit", "exit"]:
            print(f"{ASSISTANT_NAME}: It has been a pleasure, {user_name}. Farewell.")
            if user_preferences["speech_enabled"]:
                Speech.speak(f"It has been a pleasure, {user_name}. Farewell.", voice_type="Wavenet-F")  
            break

        ai_response = generate_ai_response(user_input, conversation_history, user_preferences)
        conversation_history.append((user_input, ai_response))

if __name__ == "__main__":
    chat_loop()
