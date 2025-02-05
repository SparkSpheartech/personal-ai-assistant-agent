import os
import logging
import memory
import security
import speech_recognition as sr
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Google Cloud TTS Credentials
GOOGLE_TTS_CLIENT = texttospeech.TextToSpeechClient()

# Kill Switch Support - Prevents Speech Processing if Security Mode is ON
def is_speech_allowed():
    """Checks if speech features are allowed based on security settings."""
    if security.is_internet_disabled():
        logging.warning("🛑 Speech functions disabled: Security mode is active.")
        return False
    return True

# === TEXT-TO-SPEECH (TTS) FUNCTION (PLAYS DIRECTLY IN PYTHON) ===
def speak(text, voice_type="en-US-Wavenet-D", speaking_rate=1.0):
    """
    Converts text to speech using Google Cloud TTS and plays it automatically within Python.
    No external applications required.
    """
    if not is_speech_allowed():
        return  # Prevent speech when kill switch is on
    
    logging.info(f"🗣️ Speaking: {text[:50]}...")  # Log partial text

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Select the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_type,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Modulate speech based on emotion (slower for serious responses)
    if any(word in text.lower() for word in ["warning", "alert", "caution"]):
        speaking_rate = 0.9  # Speak slower for serious messages
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate
    )

    # Generate Speech
    response = GOOGLE_TTS_CLIENT.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Convert binary audio to playable format
    audio_data = response.audio_content
    temp_audio_file = "temp_speech_output.wav"

    with open(temp_audio_file, "wb") as out:
        out.write(audio_data)

    # Load and play the audio file directly in Python
    audio = AudioSegment.from_wav(temp_audio_file)
    play(audio)

    # Cleanup temporary file
    os.remove(temp_audio_file)

# === SPEECH RECOGNITION (VOICE INPUT) FUNCTION ===
def listen():
    """
    Uses speech recognition to capture voice input.
    Returns transcribed text.
    """
    if not is_speech_allowed():
        return "Speech is disabled due to security settings."

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        logging.info("🎙️ Listening for voice input...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            logging.info(f"🗣️ Recognized: {user_input}")
            return user_input
        except sr.UnknownValueError:
            logging.warning("🤷 Speech Recognition: Could not understand audio.")
            return "I didn't catch that. Could you repeat?"
        except sr.RequestError:
            logging.error("🚫 Speech Recognition: API unavailable.")
            return "Speech recognition is currently unavailable."

# === MEMORY INTEGRATION ===
def save_speech_preference(user_name, enable_speech):
    """Saves user's speech preference in memory."""
    memory.update_user_preference(user_name, "speech_enabled", enable_speech)

def get_speech_preference(user_name):
    """Retrieves user's speech preference from memory."""
    prefs = memory.get_user_profile(user_name)
    return prefs.get("speech_enabled", False) if prefs else False

# === ADMIN OVERRIDE FOR SPEECH SETTINGS ===
def admin_toggle_speech():
    """
    Allows an admin to manually enable/disable speech functions.
    """
    current_status = is_speech_allowed()
    new_status = not current_status

    if new_status:
        security.enable_internet()  # Enable speech-related services
        logging.info("✅ Admin enabled speech functions.")
        return "Speech features have been enabled."
    else:
        security.disable_internet()  # Block speech-related services
        logging.warning("🛑 Admin disabled speech functions.")
        return "Speech features have been disabled."

if __name__ == "__main__":
    print("🎙️ Speech module initialized!")
    test_text = "Hello, this is OYNX. I am ready to assist you."
    speak(test_text)
