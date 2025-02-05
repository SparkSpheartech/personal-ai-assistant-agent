import os
import logging
import memory
import fetch_google
import security  # ✅ Import security for internet kill switch

# ✅ Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Load Kill Switch for Internet Access (Set in Environment Variables)
INTERNET_KILL_SWITCH = os.getenv("INTERNET_KILL_SWITCH", "OFF").upper() == "ON"

def process_query(user_query):
    """
    1. Checks if the query exists in memory.
    2. If found, return the saved response.
    3. If not found, fetch from Google (if allowed), save it, and return.
    4. Handles invalid inputs appropriately.
    """

    # ✅ Ignore empty inputs or non-question statements
    if not user_query.strip():
        return "❌ OYNX: Please enter a valid question or query."

    common_phrases = ["hi", "hello", "hey", "how are you", "good morning", "good night"]
    if user_query.lower() in common_phrases:
        return f"🤖 OYNX: Hello! How can I assist you today?"

    try:
        # ✅ Step 1: Check memory first
        past_response = memory.get_from_memory(user_query)
        if past_response:
            logging.info(f"✅ Retrieved from memory: {user_query}")
            return f"(💾 Retrieved from memory) {past_response}"

        # ✅ Step 2: Check if the Kill Switch is active before making a network request
        if INTERNET_KILL_SWITCH or security.is_internet_disabled():
            logging.warning("⚠️ Kill switch activated: Internet access blocked.")
            return "❌ OYNX: Internet access is currently disabled. Try again later."

        # ✅ Step 3: Fetch new result from Google
        logging.info(f"🔎 Fetching new results for query: {user_query}")
        result = fetch_google.fetch_google_content(user_query)

        # ✅ Step 4: Handle API response properly
        if isinstance(result, dict) and result.get("status") == "success":
            formatted_results = result.get("formatted_results", "No relevant information found.")

            # ✅ Save to memory for future queries
            memory.save_to_memory(user_query, formatted_results)

            return formatted_results  # ✅ Return the response

        else:
            logging.warning(f"⚠️ Google fetch failed for query: {user_query}")
            return f"❌ OYNX: Sorry, I couldn't find anything relevant for '{user_query}'. Try rephrasing your question!"

    except Exception as e:
        logging.exception(f"⚠️ Unexpected error processing query: {user_query}")
        return "⚠️ OYNX: An error occurred while processing your request. Please try again later."

# ✅ If running as standalone script
if __name__ == "__main__":
    test_query = "Quantum Computing"

    print("🔎 Processing Query...")
    response = process_query(test_query)
    print(response)
