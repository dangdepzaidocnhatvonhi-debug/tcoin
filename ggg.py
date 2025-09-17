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
URL = "https://vps.sillydevelopment.co.uk"

# Đường dẫn đến file cookie
COOKIE_FILE = "cookies.json"

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

def load_cookies(driver):
    """Tải cookie từ file"""
    try:
        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)
        driver.get(URL)  # Truy cập URL trước để set domain
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("Đã tải cookie")
        print("Đã tải cookie")
    except Exception as e:
        logging.error(f"Lỗi khi tải cookie: {e}")
        print(f"Lỗi khi tải cookie: {e}")

def kiem_tra_web():
    """Scrape trang cá nhân với cookie"""
    driver = setup_driver()
    try:
        # Tải cookie và truy cập dashboard
        load_cookies(driver)
        driver.get(URL)
        time.sleep(5)  # Đợi dashboard load

        # Kiểm tra đăng nhập thành công
        try:
            profile_name = driver.find_element(By.CLASS_NAME, "user-profile").text  # Thay bằng class thật
            logging.info(f"Tên tài khoản: {profile_name}")
            print(f"Tên tài khoản: {profile_name}")
        except:
            logging.error("Không tìm thấy tên tài khoản. Cookie có thể hết hạn.")
            print("Không tìm thấy tên tài khoản. Cookie có thể hết hạn.")
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
