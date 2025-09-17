from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import logging

# Cấu hình logging để lưu log
logging.basicConfig(filename='bot_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Thông tin đăng nhập (thay bằng thông tin thật)
USERNAME = "phengfff333@gmail.com"  # Thay bằng email/username của bạn
PASSWORD = "hoilamchi"          # Thay bằng mật khẩu

# URL dashboard
URL = "https://panel.sillydev.co.uk/store/credits"

def setup_driver():
    """Khởi tạo driver Chrome ở chế độ headless"""
    options = Options()
    options.add_argument('--headless')  # Chạy ngầm
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')  # Cần cho Render
    options.add_argument('--disable-dev-shm-usage')  # Cần cho Render
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
    driver = webdriver.Chrome(options=options)
    return driver

def kiem_tra_web():
    """Đăng nhập và scrape trang cá nhân"""
    driver = setup_driver()
    try:
        # Truy cập trang đăng nhập
        driver.get(URL)
        time.sleep(2)  # Đợi load

        # Điền email/username
        username_field = driver.find_element(By.ID, "email")  # Thay 'email' bằng ID thật (inspect F12)
        username_field.send_keys(USERNAME)
        
        # Điền password
        password_field = driver.find_element(By.ID, "password")  # Thay 'password' bằng ID thật
        password_field.send_keys(PASSWORD)
        
        # Nhấn nút đăng nhập
        login_button = driver.find_element(By.CLASS_NAME, "btn-login")  # Thay 'btn-login' bằng class thật
        login_button.click()
        time.sleep(5)  # Đợi dashboard load

        # Scrape tên tài khoản
        try:
            profile_name = driver.find_element(By.CLASS_NAME, "user-profile").text  # Thay 'user-profile'
            logging.info(f"Tên tài khoản: {profile_name}")
            print(f"Tên tài khoản: {profile_name}")
        except:
            logging.error("Không tìm thấy tên tài khoản")
            print("Không tìm thấy tên tài khoản")

        # Scrape trạng thái server
        try:
            servers = driver.find_elements(By.CLASS_NAME, "server-status")  # Thay 'server-status'
            for server in servers:
                status = server.text
                logging.info(f"Server status: {status}")
                print(f"Server status: {status}")
                if "Offline" in status:
                    logging.warning("Cảnh báo: Server offline!")
                    print("Cảnh báo: Server offline!")
                    # Thêm code gửi thông báo Discord/email
        except:
            logging.error("Không tìm thấy server")
            print("Không tìm thấy server")

    except Exception as e:
        logging.error(f"Lỗi khi scrape: {e}")
        print(f"Lỗi: {e}")
    
    finally:
        driver.quit()  # Đóng trình duyệt

# Vòng lặp để treo bot
print("Bắt đầu bot treo trang cá nhân sillydev.co.uk...")
while True:
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Đang kiểm tra...")
    kiem_tra_web()
    time.sleep(300)  # Kiểm tra mỗi 5 phút để tránh spam
