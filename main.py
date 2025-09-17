import requests
import time
import json
import os
import base64
import random
from colorama import Fore, Style, init
from datetime import datetime
try:
    import cloudscraper
except ImportError:
    cloudscraper = None
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError:
    webdriver = None

# Initialize colorama
init(autoreset=True)

# Proxy list (new free proxies, HTTP/HTTPS, low latency <500ms, updated 17/09/2025)
PROXY_LIST = [
    {'http': 'http://47.74.152.29:8888', 'https': 'http://47.74.152.29:8888'},  # ProxyScrape, US, anonymous
    {'http': 'http://185.199.229.156:7492', 'https': 'http://185.199.229.156:7492'},  # Proxifly, EU, elite
    {'http': 'http://185.199.231.45:8382', 'https': 'http://185.199.231.45:8382'},  # Proxifly, EU, elite
    {'http': 'http://72.10.164.178:15759', 'https': 'http://72.10.164.178:15759'},  # Geonode, US, anonymous
    {'http': 'http://213.157.192.33:3128', 'https': 'http://213.157.192.33:3128'},  # Geonode, EU, anonymous
]

# Test proxy before use
def test_proxy(proxy):
    try:
        response = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Proxy {proxy['http']} is working{Style.RESET_ALL}")
            return True
        return False
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}Proxy {proxy['http']} failed during test{Style.RESET_ALL}")
        return False

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

# Get headers using Selenium (fallback if proxies fail)
def get_selenium_headers(api_key):
    if not webdriver:
        print(f"{Fore.RED}Error: Selenium not installed. Install selenium and webdriver-manager.{Style.RESET_ALL}")
        return None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.get('https://panel.sillydev.co.uk/store/credits')
        time.sleep(5)  # Wait for Cloudflare challenge
        headers = {
            'User-Agent': driver.execute_script('return navigator.userAgent'),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://panel.sillydev.co.uk',
            'Referer': 'https://panel.sillydev.co.uk/store/credits',
            'X-Requested-With': 'XMLHttpRequest',
            'Authorization': f'Bearer {api_key}',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        driver.quit()
        return headers
    except Exception as e:
        print(f"{Fore.RED}Error: Selenium failed - {e}{Style.RESET_ALL}")
        return None

# Farm coins for a user
def farm_coins(api_key, color_code, max_retries=5):
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
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    # Initialize cloudscraper
    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False,
            'desktop': True
        },
        delay=10,
        debug=True
    ) if cloudscraper else requests.Session()
    
    # Test and select working proxies
    working_proxies = [proxy for proxy in PROXY_LIST if test_proxy(proxy)]
    if not working_proxies:
        print(f"{Fore.RED}Error: No working proxies available. Falling back to no proxy.{Style.RESET_ALL}")
        proxies = None
    else:
        proxies = random.choice(working_proxies)
        print(f"{Fore.YELLOW}Using proxy: {proxies['http']}{Style.RESET_ALL}")

    for attempt in range(max_retries):
        if proxies:
            print(f"{Fore.YELLOW}Attempt {attempt + 1}/{max_retries} with proxy: {proxies['http']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Attempt {attempt + 1}/{max_retries} without proxy{Style.RESET_ALL}")
        try:
            response = session.post(url, headers=headers, json={}, timeout=20, proxies=proxies)
            if response.status_code == 200:
                print(f"{Fore.BLUE + Style.BRIGHT}Success: Earned coins! Response: {response.text}{Style.RESET_ALL}")
                return True
            elif response.status_code == 401:
                print(f"{Fore.RED}Error: Invalid token - Check your API key{Style.RESET_ALL}")
                return False
            elif response.status_code == 403:
                print(f"{Fore.RED}Error: Cloudflare blocked - {response.text[:200]}{Style.RESET_ALL}")
                if attempt < max_retries - 1 and working_proxies:
                    proxies = random.choice(working_proxies)
                    continue
                # Fallback to Selenium if proxies fail
                print(f"{Fore.YELLOW}Attempting Selenium fallback...{Style.RESET_ALL}")
                selenium_headers = get_selenium_headers(decoded_key)
                if not selenium_headers:
                    return False
                response = requests.post(url, headers=selenium_headers, json={}, timeout=20, proxies=None)
                if response.status_code == 200:
                    print(f"{Fore.BLUE + Style.BRIGHT}Success: Earned coins (Selenium)! Response: {response.text}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}Error: Selenium failed - {response.status_code} - {response.text[:200]}{Style.RESET_ALL}")
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
            print(f"{Fore.RED}Error: Request failed with proxy {proxies['http'] if proxies else 'none'} - {e}{Style.RESET_ALL}")
            if attempt < max_retries - 1 and working_proxies:
                proxies = random.choice(working_proxies)
                time.sleep(5)
                continue
            return False
    print(f"{Fore.RED}Error: All attempts failed after {max_retries} retries{Style.RESET_ALL}")
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
