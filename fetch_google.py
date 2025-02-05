import os
import requests
import logging
import sqlite3
import time
import wikipediaapi
import arxiv
import security  # ✅ Security Kill Switch

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Database for Search Caching
SEARCH_STORAGE_DIR = "./search_storage"
DB_FILE = os.path.join(SEARCH_STORAGE_DIR, "search_cache.db")
os.makedirs(SEARCH_STORAGE_DIR, exist_ok=True)  # Ensure storage directory exists

# ✅ Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia("en")

def initialize_cache_db():
    """Creates a cache table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS search_cache (
                                query TEXT PRIMARY KEY,
                                response TEXT,
                                timestamp INTEGER
                              )''')
            conn.commit()
            logging.info("✅ Search cache database initialized.")
    except sqlite3.Error as e:
        logging.error(f"⚠️ Search cache initialization failed: {e}")

initialize_cache_db()

def get_cached_result(query, cache_duration=3600):
    """Checks the cache for a saved Google search result."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response, timestamp FROM search_cache WHERE query=?", (query,))
            result = cursor.fetchone()
            if result:
                saved_response, timestamp = result
                if time.time() - timestamp < cache_duration:
                    logging.info(f"💾 Retrieved from cache: {query}")
                    return eval(saved_response)
            return None
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error retrieving from cache: {e}")
        return None

def save_to_cache(query, response):
    """Saves a search response to the cache database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO search_cache (query, response, timestamp) VALUES (?, ?, ?)",
                           (query, str(response), int(time.time())))
            conn.commit()
            logging.info(f"✅ Cached search result: {query}")
    except sqlite3.Error as e:
        logging.error(f"⚠️ Error saving to cache: {e}")

def fetch_wikipedia_content(search_query):
    """Fetches Wikipedia summaries for relevant topics."""
    if security.is_internet_disabled():
        logging.warning("⚠️ Kill switch activated: Wikipedia search blocked.")
        return {"status": "error", "message": "Internet access is currently disabled."}

    try:
        page = wiki_wiki.page(search_query)
        if page.exists():
            summary = page.summary[:1000]  # Limit to 1000 characters for brevity
            return {"status": "success", "formatted_results": f"📖 Wikipedia: {summary}"}
        else:
            return {"status": "error", "message": "No Wikipedia article found."}
    except Exception as e:
        logging.error(f"⚠️ Wikipedia search failed: {e}")
        return {"status": "error", "message": "Wikipedia search error."}

def fetch_arxiv_content(search_query, max_results=3):
    """Fetches academic papers related to the search query from Arxiv."""
    if security.is_internet_disabled():
        logging.warning("⚠️ Kill switch activated: Arxiv search blocked.")
        return {"status": "error", "message": "Internet access is currently disabled."}

    try:
        search = arxiv.Search(query=search_query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        papers = list(search.results())
        if not papers:
            return {"status": "error", "message": "No academic papers found."}
        formatted_results = "🧠 **Academic Papers from Arxiv:**\n\n"
        for paper in papers:
            formatted_results += f"🔹 **{paper.title}**\n"
            formatted_results += f"📌 {paper.summary[:200]}...\n"
            formatted_results += f"🔗 [Read More]({paper.entry_id})\n\n"
        return {"status": "success", "formatted_results": formatted_results}
    except Exception as e:
        logging.error(f"⚠️ Arxiv search failed: {e}")
        return {"status": "error", "message": "Arxiv search error."}

def fetch_google_content(search_query, num_results=5):
    """Fetches Google search results with HTTPS filtering."""
    
    if security.is_internet_disabled():
        logging.warning("⚠️ Kill switch activated: Google search blocked.")
        return {"status": "error", "message": "Internet access is currently disabled."}

    cached_result = get_cached_result(search_query)
    if cached_result:
        return cached_result  

    try:
        logging.info(f"🔎 Searching Google for: {search_query}")
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": os.getenv("GOOGLE_API_KEY"), "cx": os.getenv("GOOGLE_CSE_ID"), "q": search_query, "num": num_results * 2}
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "items" not in data:
            return {"status": "error", "message": "No results found"}
        results = []
        for item in data["items"]:
            title = item.get("title", "No title available")
            snippet = item.get("snippet", "No snippet available")
            link = item.get("link", "No URL available")
            if link.startswith("https://"):
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                results.append({"title": title, "content": snippet, "url": link})
            if len(results) >= num_results:
                break
        if not results:
            return {"status": "error", "message": "No HTTPS search results available."}
        formatted_results = "**🔍 Google Search Results:**\n\n"
        for i, res in enumerate(results, 1):
            formatted_results += f"🔹 **{res['title']}**\n"
            formatted_results += f"📌 {res['content']}\n"
            formatted_results += f"🔗 [Read More]({res['url']})\n\n"
        response_data = {"status": "success", "formatted_results": formatted_results}
        save_to_cache(search_query, response_data)
        return response_data
    except requests.exceptions.RequestException as e:
        logging.error(f"⚠️ Google API request failed: {e}")
        return {"status": "error", "message": "Google search API request failed"}

if __name__ == "__main__":
    test_query = "Quantum Computing"

    # ✅ Enforce Security Protocols
    if security.is_internet_disabled():
        print("🚫 Internet access is disabled. Online features will not work.")

    print(fetch_google_content(test_query))
    print(fetch_wikipedia_content(test_query))
    print(fetch_arxiv_content(test_query))
