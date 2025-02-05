import os
import sqlite3
import requests
from search import process_query  # ✅ Correct Function
import logging
import urllib.parse
import fetch_google
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from ebooklib import epub
from openai import OpenAI

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# LM Studio AI Client
client = OpenAI(base_url="http://127.0.0.1:1234/V1", api_key="lm-studio")
MODEL = "deepseek-r1-distill-qwen-7b"

# Database File & Secure Download Directory
DB_FILE = "memory.db"
DOWNLOAD_DIR = "secure_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Book Sources
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

        cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge (
                            topic TEXT PRIMARY KEY,
                            content TEXT NOT NULL
                          )''')
        conn.commit()

initialize_db()

# === SECURE DOWNLOAD FUNCTION ===
def download_book_securely(book_data):
    """Asks user for confirmation and securely downloads a book."""
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
        print(f"❌ Download Failed: {e}")
        return None

# === BOOK TEXT EXTRACTION ===
def extract_text_from_pdf(file_path):
    try:
        return extract_text(file_path)[:10000]  
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
        return None

def extract_text_from_epub(file_path):
    try:
        book = epub.read_epub(file_path)
        text = ""
        for item in book.items:
            if isinstance(item, epub.EpubHtml):
                soup = BeautifulSoup(item.content, "html.parser")
                text += soup.get_text() + "\n"
        return text[:10000]  
    except Exception as e:
        logging.error(f"Failed to extract text from EPUB: {e}")
        return None

def extract_book_text(file_path, file_format):
    """Extracts text from a book."""
    if file_format.lower() == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_format.lower() == "epub":
        return extract_text_from_epub(file_path)
    else:
        return None

# === AI-POWERED CHAT MODE WITH CONTINUOUS LEARNING ===
def store_knowledge(topic, content):
    """Stores extracted knowledge in the database for future AI responses."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO knowledge (topic, content) VALUES (?, ?)", (topic, content))
        conn.commit()

def retrieve_knowledge(topic):
    """Retrieves stored knowledge from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM knowledge WHERE topic=?", (topic,))
        row = cursor.fetchone()
        return row[0] if row else None

def ai_chat_mode(query):
    """Uses stored knowledge and AI model to answer user queries in real-time."""
    stored_knowledge = retrieve_knowledge(query)

    if stored_knowledge:
        print(f"💡 Using stored knowledge on '{query}'")
        knowledge_base = stored_knowledge
    else:
        print(f"🌎 Fetching AI knowledge for '{query}'")
        knowledge_base = "No prior knowledge stored."

    prompt = f"""
    You are an expert AI. Answer the following user query using both stored knowledge and general AI understanding.

    Query: {query}

    Stored Knowledge:
    {knowledge_base}

    Provide a **concise and expert** response.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": prompt}]
    )

    answer = response.choices[0].message.content  # ✅ Correct

    
    if stored_knowledge is None:
        store_knowledge(query, answer)

    return answer

# === TESTING ===
if __name__ == "__main__":
    while True:
        user_input = input("\n💬 Ask me anything (type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        # Secure Book Search
        search_results = process_query(user_input)
        print(search_results)

        # AI Chat Mode with Continuous Learning
        print("\n🤖 AI Answer:")
        print(ai_chat_mode(user_input))
