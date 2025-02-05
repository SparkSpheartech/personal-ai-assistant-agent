import sqlite3
import os
import json
import logging
from chromadb import PersistentClient
import security  # 🔹 Import security module
from collections import deque
from rapidfuzz import process  # 🔹 For fuzzy matching

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database Files
MEMORY_STORAGE_DIR = "./memory_storage"  # Change the location
DB_FILE = os.path.join(MEMORY_STORAGE_DIR, "memory.db")  # Change the location
VECTOR_DB_DIR = os.path.join(MEMORY_STORAGE_DIR, "vector_memory")
os.makedirs(MEMORY_STORAGE_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# AI Context Memory (Dynamically Expands Based on Conversation)
chat_memory = deque(maxlen=10)  # 🔹 Maintains dynamic context (starts with 10)

# === Initialize Database ===
def initialize_db():
    """Creates necessary tables if they don't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                user_message TEXT NOT NULL,
                                bot_response TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                              )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL,
                                preferences TEXT NOT NULL DEFAULT '{"search_enabled": true, "ai_response_mode": "friendly"}'
                              )''')
            conn.commit()
            logging.info("✅ Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"⚠️ Database initialization failed: {e}")

initialize_db()

# === MEMORY FUNCTIONS ===
def adjust_memory_depth(user_input):
    """Dynamically adjusts memory recall depth based on conversation complexity."""
    length = len(user_input.split())  # Word count in user input

    if length < 5:
        return 5  # Short responses → Keep memory small
    elif length < 20:
        return 10  # Medium responses → Moderate memory
    elif length < 50:
        return 15  # Longer responses → Deeper recall
    else:
        return 20  # Technical discussions → Full recall

def save_to_memory(user_id, user_message, bot_response):
    """Stores user queries and chatbot responses in SQLite and VectorDB."""
    
    if security.is_internet_disabled():  # 🔹 Prevents external database interactions
        logging.warning("⚠️ Memory save blocked: Internet access is disabled.")
        return "Internet access is disabled. Memory save restricted."

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversations (user_id, user_message, bot_response) VALUES (?, ?, ?)",
                           (user_id, user_message, bot_response))
            conn.commit()
        vector_collection.add(documents=[user_message], metadatas=[{"response": bot_response}])
    except sqlite3.Error as e:
        logging.error(f"⚠️ Failed to save conversation: {e}")

    # 🔹 Store interaction in AI Context Memory
    chat_memory.append(f"User: {user_message}\nAI: {bot_response}")

def get_from_memory(user_id, user_query):
    """Retrieve the most relevant chatbot response using Hybrid Search."""
    
    if security.is_internet_disabled():  # 🔹 Ensures offline memory retrieval only
        logging.info("🔒 Using offline memory only. Internet access is disabled.")
    
    try:
        memory_depth = adjust_memory_depth(user_query)  # 🔹 Dynamic memory expansion

        # 🔹 Get past responses from SQLite (Keyword Search)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_message, bot_response FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, memory_depth))
            past_conversations = cursor.fetchall()

        if not past_conversations:
            return "I don’t recall anything related to that."

        # 🔹 Extract user messages for fuzzy matching
        past_messages = [conv[0] for conv in past_conversations]

        # 🔹 Find the closest match using fuzzy matching
        best_match, score = process.extractOne(user_query, past_messages)
        
        if score < 60:  # Adjust threshold as needed
            return "No relevant memory found."

        # 🔹 Find corresponding bot response
        for conv in past_conversations:
            if conv[0] == best_match:
                return conv[1]

        return "No relevant memory found."

    except sqlite3.Error as e:
        logging.error(f"⚠️ Error retrieving from memory: {e}")
        return None

def retrieve_full_context(user_id, user_input):
    """Retrieves past conversations dynamically based on complexity."""
    memory_depth = adjust_memory_depth(user_input)  # 🔹 Adjust memory recall depth

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, bot_response FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, memory_depth))
        past_conversations = cursor.fetchall()

    if not past_conversations:
        return "No past interactions found."

    conversation_history = []
    for conv in past_conversations:
        conversation_history.append({"role": "user", "content": conv[0]})
        conversation_history.append({"role": "assistant", "content": conv[1]})

    return conversation_history

def format_response(bot_response):
    """Formats AI responses with markdown for better readability."""
    formatted_response = f"""
    **🤖 AI Response:**
    ------------------------------
    🔹 {bot_response}
    ------------------------------
    """
    return formatted_response

# === USER PROFILE FUNCTIONS ===
def create_user_profile(name):
    """Creates a new user profile with default preferences."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO user_profiles (name, preferences) VALUES (?, ?) ",
                           (name, '{"search_enabled": true, "ai_response_mode": "friendly"}'))
            conn.commit()
            return f"Profile created for {name}! ✅"
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error creating user profile: {e}")
        return "Error creating profile."

def get_user_profile(name):
    """Retrieves user preferences by name."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT preferences FROM user_profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error retrieving user profile: {e}")
        return None

def update_user_preference(name, preference_key, preference_value):
    """Updates a user's specific preference setting."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            existing_prefs = get_user_profile(name)
            if not existing_prefs:
                return "User profile not found."
            existing_prefs[preference_key] = preference_value
            updated_prefs = json.dumps(existing_prefs)
            cursor.execute("UPDATE user_profiles SET preferences = ? WHERE name = ?", (updated_prefs, name))
            conn.commit()
            return f"Preference '{preference_key}' updated to {preference_value} for {name}. ✅"
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error updating user preference: {e}")
        return "Error updating preference."

if __name__ == "__main__":
    print("🧠 Memory module initialized with VectorDB! ✅")

    if security.is_internet_disabled():
        print("🛑 Internet access is disabled. Running in offline mode.")
