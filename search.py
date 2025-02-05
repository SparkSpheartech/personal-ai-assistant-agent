import logging
import memory
import fetch_google

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_query(user_query):
    """
    1. Check if the query exists in memory (SQLite/JSON).
    2. If found, return the saved response.
    3. If not found, fetch from Google, save it, and return.
    4. Handles invalid inputs appropriately.
    """
    
    # Ignore empty inputs or non-question statements
    if not user_query.strip():
        return "❌ OYNX: Please enter a valid question or query."

    common_phrases = ["hi", "hello", "hey", "how are you", "good morning", "good night"]
    if user_query.lower() in common_phrases:
        return f"🤖 OYNX: Hello! How can I assist you today?"

    try:
        # Step 1: Check memory first
        past_response = memory.get_from_memory(user_query)
        if past_response:
            logging.info(f"Retrieved from memory: {user_query}")
            return f"(💾 Retrieved from memory) {past_response}"

        # Step 2: Fetch new result from Google
        logging.info(f"Fetching new results for query: {user_query}")
        result = fetch_google.fetch_google_content(user_query)

        # Step 3: Handle API response properly
        if isinstance(result, dict) and result.get("status") == "success":
            title = result.get("title", "No title available")
            content = result.get("content", "No content found")
            url = result.get("url", "No URL provided")

            # Prepare response
            answer = f"**{title}**\n{content}\n🔗 {url}"
            
            # Save to memory for future queries
            memory.save_to_memory(user_query, answer)
            return answer

        else:
            logging.warning(f"Google fetch failed for query: {user_query}")
            return f"❌ OYNX: Sorry, I couldn't find anything relevant for '{user_query}'. Try rephrasing your question!"

    except Exception as e:
        logging.exception(f"Unexpected error processing query: {user_query}")
        return "⚠️ OYNX: An error occurred while processing your request. Please try again later."
