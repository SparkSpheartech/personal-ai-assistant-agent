import security
import memory
import os
import logging

# ✅ Configure Logging
LOG_FILE = "oynx.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Admin Credentials (Modify as Needed)
ADMIN_CREDENTIALS = {
    "admin": "password123",  # Default admin account
}

def authenticate_admin():
    """Authenticates admin before granting access."""
    print("\n🔒 **Admin Login Required**")
    username = input("👤 Enter Admin Username: ").strip()
    password = input("🔑 Enter Admin Password: ").strip()

    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        logging.info(f"✅ Admin '{username}' logged in.")
        print(f"✅ Welcome, {username}! Access Granted.")
        return True
    else:
        logging.warning(f"❌ Unauthorized admin access attempt: {username}")
        print("❌ Invalid credentials. Access Denied.")
        return False

def admin_dashboard():
    """Admin control panel for managing OYNX."""
    if not authenticate_admin():
        return

    while True:
        print("\n⚙️ **Admin Dashboard**")
        print("1️⃣ View All Users")
        print("2️⃣ Reset User Preferences")
        print("3️⃣ Enable/Disable Internet Access")
        print("4️⃣ View System Logs")
        print("5️⃣ Shutdown OYNX")
        print("6️⃣ Exit Admin Mode")

        choice = input("\n💡 Select an option: ").strip()

        if choice == "1":
            view_all_users()
        elif choice == "2":
            reset_user_preferences()
        elif choice == "3":
            toggle_internet_access()
        elif choice == "4":
            view_logs()
        elif choice == "5":
            shutdown_oynx()
        elif choice == "6":
            print("🔒 Exiting Admin Mode...")
            break
        else:
            print("❌ Invalid selection. Try again.")

# === ✅ ADMIN FEATURES ===
def view_all_users():
    """Displays a list of all users stored in memory."""
    users = memory.get_all_users()
    
    if users:
        print("\n📜 **Registered Users:**")
        for user in users:
            print(f"- {user}")
    else:
        print("❌ No users found.")

def reset_user_preferences():
    """Allows admin to reset user preferences."""
    user_name = input("\n👤 Enter username to reset: ").strip()
    if memory.reset_user_profile(user_name):
        logging.info(f"🔄 User {user_name} preferences reset.")
        print(f"✅ Preferences for {user_name} have been reset.")
    else:
        logging.warning(f"❌ User {user_name} not found.")
        print(f"❌ User {user_name} not found.")

def toggle_internet_access():
    """Allows admin to enable/disable internet access."""
    if security.is_internet_disabled():
        security.enable_internet()
        logging.info("🌐 Internet access enabled by Admin.")
        print("🌐 Internet access enabled.")
    else:
        security.disable_internet()
        logging.warning("🛑 Internet access disabled by Admin.")
        print("🛑 Internet access disabled.")

def view_logs():
    """Displays system logs for debugging and monitoring."""
    try:
        with open(LOG_FILE, "r") as log_file:
            logs = log_file.readlines()
            print("\n📜 **System Logs:**")
            for log in logs[-10:]:  # Show last 10 log entries
                print(log.strip())
    except FileNotFoundError:
        print("❌ Log file not found.")

def shutdown_oynx():
    """Shuts down OYNX."""
    print("⚠️ OYNX is shutting down...")
    logging.critical("⚠️ OYNX shutdown initiated by Admin.")
    os._exit(0)  # Force shutdown

# ✅ Retrieve All Users from Database
def get_all_users():
    """Fetches all usernames from the user database."""
    with sqlite3.connect(memory.DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM user_profiles")
        users = cursor.fetchall()
    
    return [user[0] for user in users] if users else []

# ✅ Reset User Profile Data
def reset_user_profile(user_name):
    """Resets user preferences to default."""
    with sqlite3.connect(memory.DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM user_profiles WHERE name = ?", (user_name,))
        if cursor.fetchone():
            default_preferences = json.dumps({"search_enabled": True, "ai_response_mode": "friendly"})
            cursor.execute("UPDATE user_profiles SET preferences = ? WHERE name = ?", (default_preferences, user_name))
            conn.commit()
            return True
    return False

if __name__ == "__main__":
    admin_dashboard()
