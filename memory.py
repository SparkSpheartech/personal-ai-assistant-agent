# memory.py - Enhanced Long-Term Memory
import sqlite3
import os
import json
import logging
from chromadb import PersistentClient

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database Files
DB_FILE = "memory.db"
VECTOR_DB_DIR = "vector_memory"
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Initialize Vector Database for Long-Term Memory
vector_client = PersistentClient(path=VECTOR_DB_DIR)
vector_collection = vector_client.get_or_create_collection(name="chat_memory")

# === Initialize Database ===
def initialize_db():
    """Creates necessary tables if they don't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
def save_to_memory(user_message, bot_response):
    """Stores user queries and chatbot responses in SQLite and VectorDB."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversations (user_message, bot_response) VALUES (?, ?)",
                           (user_message, bot_response))
            conn.commit()
        vector_collection.add(documents=[user_message], metadatas=[{"response": bot_response}])
    except sqlite3.Error as e:
        logging.error(f"⚠️ Failed to save conversation: {e}")


def get_from_memory(user_query):
    """Retrieve the most relevant chatbot response from VectorDB or SQLite."""
    try:
        results = vector_collection.query(query_texts=[user_query], n_results=1)
        if results["documents"]:
            return results["metadatas"][0]["response"]
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bot_response FROM conversations WHERE user_message = ? ORDER BY timestamp DESC LIMIT 1", (user_query,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error retrieving from memory: {e}")
        return None

# === USER PROFILE FUNCTIONS ===
def create_user_profile(name):
    """Creates a new user profile with default preferences."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO user_profiles (name, preferences) VALUES (?, ?)",
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
