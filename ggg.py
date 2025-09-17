from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import logging
import json
import os

# Cấu hình logging
logging.basicConfig(filename='bot_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# URL dashboard
URL = "https://panel.sillydev.co.uk/auth/login"
COOKIE_FILE = "cookies.json"

# Thông tin đăng nhập (lưu trong biến môi trường trên Render)
USERNAME = os.getenv('SILLYDEV_USERNAME', 'phengfff333@gmail.com')
PASSWORD = os.getenv('SILLYDEV_PASSWORD', 'your_password')

def setup_driver():
    """Khởi tạo driver Chrome headless"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')  # Cần cho Render
    options.add_argument('--disable-dev-shm-usage')  # Cần cho Render
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
    driver = webdriver.Chrome(options=options)
    return driver

def login_and_save_cookies(driver):
    """Đăng nhập và lưu cookie mới"""
    try:
        driver.get(URL)
        time.sleep(2)
        driver.find_element(By.ID, "login_email").send_keys(USERNAME)
        driver.find_element(By.ID, "login_password").send_keys(PASSWORD)
        driver.find_element(By.ID, "login_button").click()
        time.sleep(5)  # Đợi dashboard load
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, 'w') as f:
            json.dump(cookies, f)
        logging.info("Đã đăng nhập và lưu cookie mới")
        print("Đã đăng nhập và lưu cookie mới")
        return cookies
    except Exception as e:
        logging.error(f"Lỗi khi đăng nhập: {e}")
        print(f"Lỗi khi đăng nhập: {e}")
        return None

def load_cookies(driver):
    """Tải cookie từ file"""
    try:
        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)
        driver.get(URL)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("Đã tải cookie")
        print("Đã tải cookie")
        return True
    except Exception as e:
        logging.error(f"Lỗi khi tải cookie: {e}")
        print(f"Lỗi khi tải cookie: {e}")
        return False

def kiem_tra_web():
    """Scrape trang cá nhân với cookie"""
    driver = setup_driver()
    try:
        # Thử tải cookie
        if not load_cookies(driver):
            cookies = login_and_save_cookies(driver)
            if not cookies:
                return

        # Truy cập dashboard
        driver.get(URL)
        time.sleep(5)

        # Kiểm tra đăng nhập
        try:
            profile_name = driver.find_element(By.CLASS_NAME, "user-profile").text  # Thay bằng class thật
            logging.info(f"Tên tài khoản: {profile_name}")
            print(f"Tên tài khoản: {profile_name}")
        except:
            logging.error("Không tìm thấy tên tài khoản. Cookie có thể hết hạn.")
            print("Không tìm thấy tên tài khoản. Cookie có thể hết hạn.")
            login_and_save_cookies(driver)
            return

        # Scrape trạng thái server
        try:
            servers = driver.find_elements(By.CLASS_NAME, "server-status")  # Thay bằng class thật
            for server in servers:
                status = server.text
                logging.info(f"Server status: {status}")
                print(f"Server status: {status}")
                if "Offline" in status:
                    logging.warning("Cảnh báo: Server offline!")
                    print("Cảnh báo: Server offline!")
                    # Thêm code gửi thông báo
        except:
            logging.error("Không tìm thấy server")
            print("Không tìm thấy server")

    except Exception as e:
        logging.error(f"Lỗi khi scrape: {e}")
        print(f"Lỗi: {e}")
    
    finally:
        driver.quit()

# Vòng lặp để treo bot
print("Bắt đầu bot treo trang cá nhân sillydev.co.uk...")
while True:
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Đang kiểm tra...")
    kiem_tra_web()
    time.sleep(300)  # Kiểm tra mỗi 5 phút
