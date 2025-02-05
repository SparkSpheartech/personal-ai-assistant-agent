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
import security
import admin
from google.cloud import texttospeech  # ✅ Google Cloud TTS
from openai import OpenAI
from speech import Speech  # ✅ Speech Control
from rapidfuzz import process  # ✅ Fuzzy matching for better mode selection

# ✅ Set Google Application Credentials explicitly in the script
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\shaza\.lmstudio\Oynx_Ai\ai-voice-449905-45464ad2e6bb.json"

# Define Assistant Name
ASSISTANT_NAME = "OYNX"

# ✅ Initialize LM Studio AI Client
client = OpenAI(base_url="http://127.0.0.1:1234/V1", api_key="lm-studio")
MODEL = "deepseek-r1-distill-qwen-7b"

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

# === Admin Mode Detection ===
def is_admin(user_name):
    """Checks if the user is an admin."""
    return user_name.lower() in admin.get_admin_list()

# === User Setup with Personality Detection ===
def detect_user_personality(user_name):
    """Suggests an AI personality based on past interactions."""
    past_conversations = memory.get_from_memory(user_name)

    if not past_conversations:
        return "Butler"  # Default personality

    if "joke" in past_conversations or "funny" in past_conversations:
        return "Comedian"
    elif "help" in past_conversations or "advice" in past_conversations:
        return "Advisor"

    return "Butler"

def setup_user():
    """Interactive startup guide for OYNX."""
    print(f"\n🎩 Welcome! I am {ASSISTANT_NAME}, your personal AI assistant.")

    user_name = input("\n💡 How shall I address you? ").strip()
    profile = memory.get_user_profile(user_name)

    if profile:
        print(f"🔄 Welcome back, {user_name}! Restoring your preferences...")
        return user_name, profile  

    print("\n🎭 Personalities Available: Butler, Advisor, Comedian")
    suggested_personality = detect_user_personality(user_name)
    chosen_personality = input(f"\n💬 I suggest '{suggested_personality}'. Keep it? (yes/no): ").strip().lower()

    if chosen_personality == "no":
        chosen_personality = input("💡 Choose your AI's personality: ").strip().capitalize()
        if chosen_personality not in ["Butler", "Advisor", "Comedian"]:
            chosen_personality = "Butler"
    else:
        chosen_personality = suggested_personality

    voice_preference = input("\n🎤 Would you like OYNX to speak? (yes/no): ").strip().lower()
    speech_enabled = voice_preference == "yes"

    user_preferences = {
        "personality": chosen_personality,
        "speech_enabled": speech_enabled,
        "search_enabled": True,
        "ai_response_enabled": True
    }
    memory.create_user_profile(user_name)
    memory.update_user_preference(user_name, "preferences", user_preferences)

    print(f"\n✅ Setup complete! Welcome, {user_name}. Personality set to **{chosen_personality}**.")
    
    if speech_enabled:
        Speech.speak(f"Welcome, {user_name}. I'm OYNX, your {chosen_personality} assistant. How can I help you today?")
    
    return user_name, user_preferences

# === Fuzzy Mode Selection for Better UX ===
def select_mode():
    """Allows users to pick a startup mode with fuzzy matching."""
    available_modes = ["Chat Mode", "Coding Assistant", "Research Mode", "Task Manager", "Admin Mode"]

    print("\n🌟 OYNX Modes Available:")
    for index, mode in enumerate(available_modes, 1):
        print(f"{index}️⃣ {mode}")

    mode_choice = input("\n💡 Choose a mode (or type name): ").strip()
    best_match, score = process.extractOne(mode_choice, available_modes)

    if score > 60:
        return best_match  
    return "Chat Mode"  

# === AI Chatbot Loop ===
def chat_loop(user_name, user_preferences):
    """Main chatbot loop with voice control."""
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
                Speech.speak(f"It has been a pleasure, {user_name}. Farewell.")  
            break

        ai_response = memory.get_from_memory(user_input) or "I'm still learning!"
        conversation_history.append((user_input, ai_response))
        print(f"\n🤖 {ASSISTANT_NAME}: {ai_response}")

# === Main Entry Point with Admin Integration ===
def start_oynx():
    """Launches OYNX with Admin Integration."""
    print("\n🛠 **OYNX Startup Menu**")
    print("1️⃣ Start OYNX")
    print("2️⃣ Enter Admin Mode")
    print("3️⃣ Exit")

    choice = input("\n💡 Select an option: ").strip()

    if choice == "1":
        user_name, user_preferences = setup_user()
        mode = select_mode()

        print(f"\n🚀 Starting {mode} for {user_name}...")

        if user_preferences["speech_enabled"]:
            Speech.speak(f"Welcome, {user_name}. Entering {mode}. How can I assist you?")

        if mode == "Chat Mode":
            chat_loop(user_name, user_preferences)
        elif mode == "Coding Assistant":
            print("🚀 Launching Coding Assistant... (Integration needed)")
        elif mode == "Research Mode":
            print("🔍 Starting Research Mode... (Integration needed)")
        elif mode == "Task Manager":
            print("📅 Opening Task Manager... (Integration needed)")
    elif choice == "2":
        admin.admin_dashboard()
    elif choice == "3":
        print("👋 Exiting...")
        exit()
    else:
        print("❌ Invalid selection. Try again.")

if __name__ == "__main__":
    start_oynx()
