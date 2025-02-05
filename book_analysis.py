import PyPDF2
import os
import logging
import memory
import ebooklib
from ebooklib import epub
from openai import OpenAI

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize AI Client (Using OYNX AI Model)
client = OpenAI(base_url="http://127.0.0.1:1234/V1", api_key="lm-studio")
MODEL = "deepseek-r1-distill-qwen-7b"  # OYNX AI Model

# === TEXT EXTRACTION FUNCTIONS ===
def extract_text_from_pdf(file_path):
    """Extracts text from a PDF book."""
    extracted_text = []
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

        return "\n".join(extracted_text) if extracted_text else None
    except Exception as e:
        logging.error(f"❌ Error extracting text from PDF: {e}")
        return None

def extract_text_from_epub(file_path):
    """Extracts text from an EPUB book."""
    extracted_text = []
    try:
        book = epub.read_epub(file_path)
        for item in book.items:
            if isinstance(item, epub.EpubHtml):
                extracted_text.append(item.content.decode("utf-8", errors="ignore"))

        return "\n".join(extracted_text) if extracted_text else None
    except Exception as e:
        logging.error(f"❌ Error extracting text from EPUB: {e}")
        return None

def extract_text_from_txt(file_path):
    """Reads text from a plain .txt book file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logging.error(f"❌ Error extracting text from TXT file: {e}")
        return None

def extract_book_text(file_path):
    """Auto-detects and extracts text from PDF, EPUB, or TXT files."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".epub"):
        return extract_text_from_epub(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        logging.warning(f"❌ Unsupported book format: {file_path}")
        return None

# === AI-ENHANCED BOOK ANALYSIS ===
def analyze_book(title):
    """Fetches book content and provides an AI-generated summary."""
    book_data = memory.get_book_by_title(title)
    if not book_data:
        return "❌ Book not found in the database."

    stored_text = memory.get_book_text(title)
    if not stored_text and book_data.get("file_path"):
        extracted_text = extract_book_text(book_data["file_path"])
        if extracted_text:
            memory.store_book_text(title, extracted_text)
            stored_text = extracted_text
        else:
            return "❌ No readable text found in the book."

    return summarize_book(title, stored_text)

def summarize_book(title, book_text):
    """Generates an AI-powered summary of the book content."""
    if not book_text:
        return "❌ No text available for summarization."

    prompt = f"""
    You are an AI book analyst. Generate a **detailed summary** of the book **{title}**.

    **Book Excerpt:**
    {book_text[:3000]}  # First 3000 characters for context

    **Summarize in key points and main themes.**
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        )

        summary = response.choices[0].message.content
        return f"📖 **Summary of {title}:**\n{summary}"

    except Exception as e:
        logging.error(f"❌ AI summarization failed: {e}")
        return "❌ Unable to generate a summary."

# === AI-POWERED READING MODE ===
def ai_read_book(title):
    """OYNX AI reads a book aloud and explains key concepts."""
    book_text = memory.get_book_text(title)

    if not book_text:
        return "❌ Book text not found in memory."

    prompt = f"""
    You are an AI audiobook assistant. Read and explain the book **{title}** interactively.
    Provide explanations in an engaging and educational style.
    
    **Book Content:**
    {book_text[:3000]}  # Use the first 3000 characters

    **Summarize each section interactively.**
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        )

        ai_narration = response.choices[0].message.content
        return f"🔊 **OYNX AI Narration:**\n{ai_narration}"

    except Exception as e:
        logging.error(f"❌ AI reading mode failed: {e}")
        return "❌ Unable to generate AI reading."

# === ADVANCED BOOK SEARCH ===
def search_books(query):
    """Searches for books by title, author, or keyword."""
    books = memory.get_all_books()
    
    matches = [book for book in books if query.lower() in book["title"].lower() or query.lower() in book["author"].lower()]
    
    if not matches:
        return "❌ No matching books found."

    result = "\n📚 **Search Results:**\n"
    for book in matches:
        result += f"- **{book['title']}** by {book['author']}\n"
    
    return result

if __name__ == "__main__":
    print("\n📖 **Book Analysis System Ready**")

    while True:
        print("\n🛠 **Book Features**")
        print("1️⃣ Analyze a Book")
        print("2️⃣ AI Reading Mode")
        print("3️⃣ Search for a Book")
        print("4️⃣ Exit")

        choice = input("\n💡 Select an option: ").strip()

        if choice == "1":
            book_title = input("\n📖 Enter book title: ").strip()
            print(analyze_book(book_title))
        elif choice == "2":
            book_title = input("\n🔊 Enter book title: ").strip()
            print(ai_read_book(book_title))
        elif choice == "3":
            search_query = input("\n🔍 Enter search term: ").strip()
            print(search_books(search_query))
        elif choice == "4":
            print("👋 Exiting Book Analysis...")
            break
        else:
            print("❌ Invalid selection. Try again.")
