import logging
import memory
import fetch_google
import security  # ✅ Ensures Kill Switch is active

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def search_query(user_query):
    """
    🔍 **Intelligent Search Process**
    1️⃣ Check if the response is already stored in memory.
    2️⃣ If found, return it instantly (avoiding unnecessary API calls).
    3️⃣ If not found and internet is enabled, fetch from Google/Wikipedia.
    4️⃣ If Kill Switch is active, restrict external API access.
    5️⃣ Store new results in memory for future efficiency.
    """

    # ✅ 1️⃣ Check Memory First
    past_response = memory.get_from_memory(user_query)
    if past_response:
        logging.info(f"💾 Retrieved from memory: {user_query}")
        return f"(💾 Memory) {past_response}"

    # ✅ 2️⃣ Check if the Kill Switch is active
    if security.is_internet_disabled():
        logging.warning("🚫 Internet access blocked. Cannot fetch new search results.")
        return "❌ OYNX: Internet is disabled. Try again later or enable online mode."

    # ✅ 3️⃣ Fetch New Data (Google, Wikipedia, ArXiv)
    logging.info(f"🔎 Searching online for: {user_query}")
    search_results = fetch_google.fetch_google_content(user_query)

    # ✅ 4️⃣ Handle API Response
    if isinstance(search_results, dict) and search_results.get("status") == "success":
        formatted_results = search_results.get("formatted_results", "No relevant information found.")

        # ✅ Save to memory for faster future searches
        memory.save_to_memory(user_query, formatted_results)
        return formatted_results

    # ✅ 5️⃣ Handle No Results Case
    logging.warning(f"⚠️ No search results found for: {user_query}")
    return f"❌ OYNX: Sorry, I couldn't find anything relevant for '{user_query}'. Try a different query."

# ✅ Run standalone for testing
if __name__ == "__main__":
    test_query = "What is Quantum Computing?"
    print(search_query(test_query))
