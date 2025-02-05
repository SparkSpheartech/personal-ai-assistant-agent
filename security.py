import os
import logging

# Configure Logging for Security
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === 🔐 INTERNET KILL SWITCH ===
INTERNET_KILL_SWITCH = os.getenv("INTERNET_KILL_SWITCH", "OFF").upper() == "ON"

def is_internet_disabled():
    """Checks if the internet kill switch is active."""
    if INTERNET_KILL_SWITCH:
        logging.warning("⚠️ Internet access is disabled. Restricted features are blocked.")
        return True
    return False

# === 🔐 ACCESS CONTROL ===
AUTHORIZED_USERS = ["admin", "Shazaly"]  # Define authorized users

def check_user_access(username):
    """Restricts access based on authorized users list."""
    if username not in AUTHORIZED_USERS:
        logging.warning(f"🚫 Unauthorized access attempt: {username}")
        return False
    return True

# === 🔐 FIREWALL RULES (Linux Example) ===
def block_internet():
    """Blocks all outgoing internet connections (Linux)."""
    os.system("sudo iptables -A OUTPUT -p tcp --dport 80 -j DROP")
    os.system("sudo iptables -A OUTPUT -p tcp --dport 443 -j DROP")
    logging.info("🔒 Internet access blocked.")

def allow_internet():
    """Allows outgoing internet connections (Linux)."""
    os.system("sudo iptables -D OUTPUT -p tcp --dport 80 -j DROP")
    os.system("sudo iptables -D OUTPUT -p tcp --dport 443 -j DROP")
    logging.info("🔓 Internet access restored.")

# === 🔐 ADMIN OVERRIDE ===
def toggle_internet_kill_switch(state):
    """Manually enables or disables the internet kill switch."""
    global INTERNET_KILL_SWITCH
    INTERNET_KILL_SWITCH = state.upper() == "ON"
    logging.info(f"🛑 Internet Kill Switch set to: {'ON' if INTERNET_KILL_SWITCH else 'OFF'}")
