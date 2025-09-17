import requests
import time
import json
import os
import base64
from colorama import Fore, Style, init
from datetime import datetime
try:
    import cloudscraper
except ImportError:
    cloudscraper = None

# Initialize colorama
init(autoreset=True)

# Proxy (optional, replace with your proxy if needed)
PROXIES = {
    'http': 'http://your_proxy_ip:port',
    'https': 'https://your_proxy_ip:port'
}  # Example: 'http://123.45.67.89:8080'

# Load users from users.json
def load_users():
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        return users
    except FileNotFoundError:
        print(f"{Fore.RED}Error: users.json not found. Please create it with your API keys.{Style.RESET_ALL}")
        return {}
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: Invalid JSON in users.json{Style.RESET_ALL}")
        return {}

# Farm coins for a user
def farm_coins(api_key, color_code):
    url = "https://panel.sillydev.co.uk/api/client/store/earncredits"
    # Decode key if encoded
    try:
        decoded_key = base64.b64decode(api_key).decode() if api_key.startswith('cHRsY18=') else api_key
    except:
        decoded_key = api_key
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://panel.sillydev.co.uk',
        'Referer': 'https://panel.sillydev.co.uk/store/credits',
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': f'Bearer {decoded_key}',
        # Add Cloudflare cookies if needed (get from browser)
        'Cookie': 'cf_clearance=your_cf_clearance_cookie_here'  # Replace with actual cf_clearance
    }
    # Initialize cloudscraper with advanced options
    session = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        delay=10,
        debug=False
    ) if cloudscraper else requests.Session()
    
    try:
        # Use proxies if provided
        response = session.post(url, headers=headers, json={}, timeout=15, proxies=PROXIES if PROXIES else None)
        if response.status_code == 200:
            print(f"{Fore.BLUE + Style.BRIGHT}Success: Earned coins! Response: {response.text}{Style.RESET_ALL}")
            return True
        elif response.status_code == 401:
            print(f"{Fore.RED}Error: Invalid token - Check your API key{Style.RESET_ALL}")
            return False
        elif response.status_code == 403:
            print(f"{Fore.RED}Error: Cloudflare blocked - {response.text[:200]}{Style.RESET_ALL}")
            return False
        elif response.status_code == 419:
            print(f"{Fore.YELLOW}Error: Token expired - Regenerate API key{Style.RESET_ALL}")
            return False
        elif response.status_code in (301, 302, 303):
            print(f"{Fore.RED}Error: Redirect detected - {response.headers.get('Location', 'Unknown')}{Style.RESET_ALL}")
            return False
        else:
            print(f"{Fore.RED}Error: {response.status_code} - {response.text[:200]}{Style.RESET_ALL}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error: Request failed - {e}{Style.RESET_ALL}")
        return False

# Main loop
def main():
    users = load_users()
    if not users:
        print("No users configured. Please add to users.json")
        return

    print("Starting SillyDev Coins Farmer...")
    for username, config in users.items():
        api_key, color_code = config
        if not api_key.startswith(('ptlc_', 'cHRsY18=')):
            print(f"{Fore.RED}Error: Invalid token for {username} - API key must start with 'ptlc_' or be base64-encoded{Style.RESET_ALL}")
            continue

        print(f"Farming for {username}...")
        success = farm_coins(api_key, color_code)
        if not success:
            print(f"Failed to farm for {username}")

    time.sleep(300)  # Wait 5 minutes to avoid rate limit

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Bot stopped by user")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(300)
