import requests
import time
import os
import base64
import json
import random
from http.cookiejar import MozillaCookieJar
from datetime import datetime
import logging

# Cấu hình logging
logging.basicConfig(filename='bot_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# URL và endpoint
URL = "https://panel.sillydevelopment.co.uk"
EARN_CREDITS_ENDPOINT = f"{URL}/api/client/store/earncredits"
LOGIN_URL = f"{URL}/auth/login"

# Thông tin đăng nhập (lưu trong biến môi trường)
USERNAME = os.getenv('SILLYDEV_USERNAME', 'phengfff333@gmail.com')
PASSWORD = os.getenv('SILLYDEV_PASSWORD', 'hoilamchi')

# File cookie
COOKIE_FILE = "ck.txt"

def login_and_save_cookies(session):
    """Đăng nhập và lưu cookie mới"""
    try:
        # Lấy XSRF-TOKEN từ trang login
        response = session.get(URL)
        xsrf_token = requests.utils.unquote(session.cookies.get('XSRF-TOKEN', ''))
        
        # Gửi request đăng nhập
        login_data = {
            'login_email': USERNAME,
            'login_password': PASSWORD,
            '_token': xsrf_token  # CSRF token
        }
        headers = {
            'Origin': URL,
            'Referer': f"{URL}/auth/login",
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = session.post(LOGIN_URL, data=login_data, headers=headers)
        
        if response.status_code == 200 or 'dashboard' in response.url:
            # Lưu cookie vào ck.txt (định dạng Netscape)
            session.cookies.save(COOKIE_FILE, ignore_discard=True, ignore_expires=True)
            logging.info("Đã đăng nhập và lưu cookie mới")
            print("Đã đăng nhập và lưu cookie mới")
            return True
        else:
            logging.error(f"Đăng nhập thất bại: {response.status_code}")
            print(f"Đăng nhập thất bại: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Lỗi khi đăng nhập: {e}")
        print(f"Lỗi khi đăng nhập: {e}")
        return False

def earn_credits():
    """Gửi request kiếm credits"""
    s = requests.Session()
    # Tải cookie từ ck.txt
    cookie_jar = MozillaCookieJar(COOKIE_FILE)
    try:
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        s.cookies.update(cookie_jar)
    except FileNotFoundError:
        logging.error("Không tìm thấy ck.txt, thử đăng nhập...")
        print("Không tìm thấy ck.txt, thử đăng nhập...")
        if not login_and_save_cookies(s):
            return

    while True:
        try:
            audio_fp = f'{random.getrandbits(32):08x}'
            canvas_fp = f'{random.getrandbits(128):032x}'
            headers = {
                'Origin': URL,
                'Referer': f'{URL}/store/credits',
                'X-Requested-With': 'XMLHttpRequest',
                'X-XSRF-TOKEN': requests.utils.unquote(s.cookies.get('XSRF-TOKEN', '')),
                'x-audio-fingerprint': audio_fp,
                'x-canvas-fingerprint': canvas_fp,
                'x-browser-verification': base64.b64encode(json.dumps({
                    "canvas": canvas_fp,
                    "audio": audio_fp,
                    "entropy": {
                        "activityScore": random.randint(80, 100),
                        "timeSinceInteraction": random.randint(1000, 6000),
                        "sessionLength": random.randint(4000, 20000),
                        "hasMouseActivity": True,
                        "hasKeyboardActivity": True,
                        "hasScrollActivity": True,
                        "hasHadActivity": True,
                        "noise": f'{random.getrandbits(24):06x}'
                    },
                    "botIndicators": [],
                    "timestamp": int(time.time() * 1000),
                    "requestId": f'{random.getrandbits(64):016x}',
                    "timezoneOffset": -420,
                    "timezoneString": "Asia/Bangkok",
                    "screenInfo": {
                        "width": 1550,
                        "height": 721,
                        "availWidth": 1550,
                        "availHeight": 680,
                        "colorDepth": 24,
                        "pixelDepth": 24
                    },
                    "navigatorInfo": {
                        "hardwareConcurrency": 4,
                        "deviceMemory": 4,
                        "platform": "Win32",
                        "languages": ["vi-VN", "vi"],
                        "connectionType": "unknown",
                        "userAgentData": [
                            {"brand": "Not;A=Brand", "version": "99"},
                            {"brand": "Google Chrome", "version": "139"},
                            {"brand": "Chromium", "version": "139"}
                        ]
                    }
                }).encode()).decode()
            }
            resp = s.post(EARN_CREDITS_ENDPOINT, headers=headers)
            
            if resp.status_code == 200:
                logging.info("Gửi request kiếm credits thành công")
                print("Gửi request kiếm credits thành công")
            elif resp.status_code == 419:
                logging.warning("Cookie hết hạn, thử đăng nhập lại...")
                print("Cookie hết hạn, thử đăng nhập lại...")
                if login_and_save_cookies(s):
                    continue
            else:
                logging.error(f"Lỗi server: {resp.status_code}")
                print(f"Lỗi server: {resp.status_code}")
        except Exception as e:
            logging.error(f"Lỗi: {e}")
            print(f"Lỗi: {e}")
        time.sleep(60)  # Delay 60s

# Chạy bot
if __name__ == "__main__":
    print("Bắt đầu bot kiếm credits trên panel.sillydev.co.uk...")
    earn_credits()
