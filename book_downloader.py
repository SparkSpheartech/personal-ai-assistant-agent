import os
import sqlite3
import requests
import logging
import urllib.parse
import fetch_google
import security  # ✅ Security Module (for kill switch)
import memory    # ✅ Memory Module (for knowledge storage)
import book_analysis  # ✅ AI-powered book processing
from search import process_query
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from ebooklib import epub
from openai import OpenAI

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize AI Client (OYNX AI Pipeline)
client = OpenAI(base_url="http://127.0.0.1:1234/V1", api_key="lm-studio")
MODEL = "deepseek-r1-distill-qwen-7b"

# ✅ Database & Secure Download Directories
DB_FILE = "data/memory.db"  # ✅ Moved to `data/` directory
DOWNLOAD_DIR = "data/secure_downloads"  # ✅ Moved to `data/`
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ Book Sources
LIBGEN_SEARCH_URL = "http://libgen.rs/search.php?req={}&res=25&columns=def"
LIBGEN_DOWNLOAD_URL = "http://library.lol/main/{}"
OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json?q={}"

# === DATABASE FUNCTIONS ===
def initialize_db():
    """Creates necessary tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            author TEXT NOT NULL,
                            year TEXT,
                            file_format TEXT DEFAULT NULL,
                            file_size TEXT DEFAULT NULL,
                            file_path TEXT DEFAULT NULL,
                            source TEXT NOT NULL,
                            extracted_text TEXT DEFAULT NULL
                          )''')
        conn.commit()

initialize_db()

# === SECURE BOOK DOWNLOAD ===
def download_book_securely(book_data):
    """Downloads a book with user confirmation and security checks."""
    
    title, author, file_format, download_url = book_data["title"], book_data["author"], book_data["file_format"], book_data["download_url"]
    
    confirm = input(f"⚠️ Do you want to download '{title}' by {author}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Download canceled.")
        return None

    file_name = f"{title} - {author}.{file_format}".replace("/", "-")
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    try:
        print(f"📥 Downloading: {title} ({file_format})...")
        response = requests.get(download_url, stream=True)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO books (title, author, file_format, file_path, source)
                              VALUES (?, ?, ?, ?, ?)""",
                           (title, author, file_format, file_path, "LibGen"))
            conn.commit()

        print(f"✅ Download Complete: {file_name}")
        return file_path

    except Exception as e:
        logging.error(f"❌ Download Failed: {e}")
        return None

# === BOOK TEXT EXTRACTION ===
def extract_text_from_book(file_path):
    """Auto-detects file format and extracts text from PDF, EPUB, or TXT."""
    return book_analysis.extract_book_text(file_path)

# === AI-POWERED KNOWLEDGE STORAGE ===
def store_knowledge(topic, content):
    """Stores extracted knowledge in the memory database."""
    memory.store_knowledge(topic, content)

def retrieve_knowledge(topic):
    """Retrieves stored knowledge from memory database."""
    return memory.retrieve_knowledge(topic)

# === AI-ENHANCED BOOK ANALYSIS ===
def analyze_book(title):
    """Analyzes book content and provides an AI summary."""
    return book_analysis.analyze_book(title)

def ai_chat_mode(query):
    """Uses stored knowledge and AI model to answer user queries in real-time."""
    
    # ✅ Check if internet access is enabled
    if security.is_internet_disabled():
        print("🛑 Internet access is disabled. Using offline knowledge only.")
        stored_knowledge = retrieve_knowledge(query) or "No prior knowledge stored."
    else:
        stored_knowledge = retrieve_knowledge(query)

    prompt = f"""
    You are an expert AI. Answer the following user query using both stored knowledge and general AI understanding.

    Query: {query}

    Stored Knowledge:
    {stored_knowledge}

    Provide a **concise and expert** response.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        )

        answer = response.choices[0].message.content  # ✅ Correct
        
        # ✅ Store new knowledge
        if stored_knowledge == "No prior knowledge stored.":
            store_knowledge(query, answer)

        return answer
    
    except Exception as e:
        logging.error(f"❌ AI response generation failed: {e}")
        return "❌ AI could not generate a response."

# === TESTING ===
if __name__ == "__main__":
    while True:
        print("\n🛠 **OYNX AI Assistant**")
        print("1️⃣ AI Chat Mode")
        print("2️⃣ Search for Books")
        print("3️⃣ Download a Book")
        print("4️⃣ Analyze a Book")
        print("5️⃣ Exit")

        choice = input("\n💡 Select an option: ").strip()

        if choice == "1":
            user_input = input("\n💬 Ask me anything: ").strip()
            print("\n🤖 AI Answer:")
            print(ai_chat_mode(user_input))
        
        elif choice == "2":
            search_query = input("\n🔍 Enter search term: ").strip()
            print("\n📚 **Search Results:**")
            print(process_query(search_query))
        
        elif choice == "3":
            print("\n📖 **Downloading Books from LibGen**")
            book_data = {
                "title": input("Enter book title: ").strip(),
                "author": input("Enter book author: ").strip(),
                "file_format": input("Enter file format (pdf/epub/txt): ").strip(),
                "download_url": input("Enter book download URL: ").strip()
            }
            download_book_securely(book_data)
        
        elif choice == "4":
            book_title = input("\n📖 Enter book title to analyze: ").strip()
            print(analyze_book(book_title))

        elif choice == "5":
            print("👋 Exiting OYNX AI Assistant...")
            break
        
        else:
            print("❌ Invalid selection. Try again.")
