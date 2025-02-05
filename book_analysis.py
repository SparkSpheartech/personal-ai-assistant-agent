import PyPDF2
import memory

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF book."""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text

def analyze_book(title):
    """Fetches the book's content and provides an AI-generated summary."""
    book_data = memory.get_book_by_title(title)
    if not book_data:
        return "Book not found in the database."

    stored_text = memory.get_book_text(title)
    if not stored_text and book_data[6]:  # file_path is at index 6
        extracted_text = extract_text_from_pdf(book_data[6])
        memory.store_book_text(title, extracted_text)
        stored_text = extracted_text

    if not stored_text:
        return "No readable text found in the book."

    return f"Summary of {title}:\n{stored_text[:1000]}..."  # First 1000 chars as preview

