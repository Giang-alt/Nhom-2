import time
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.shortcuts import render

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

# Biến lưu log để hiển thị trên web
TEST_LOGS = []

def log_message(level, message):
    """Ghi log và lưu vào danh sách để hiển thị trên web"""
    log_entry = f"{level} - {message}"
    TEST_LOGS.append(log_entry)
    logging.log(level, message)

def run_selenium_test():
    """Chạy AutoTest đăng nhập bằng Selenium"""
    log_message(logging.INFO, "🚀 Khởi động trình duyệt Chrome...")
    driver = webdriver.Chrome()

    try:
        # Mở trang đăng nhập
        driver.get("http://127.0.0.1:8000/login/")
        log_message(logging.INFO, "🌍 Đã mở trang đăng nhập")
        time.sleep(3)  # Chờ trang load

        # Nhập username
        inputUserName = driver.find_element(By.NAME, "username")
        inputUserName.send_keys("user15")
        log_message(logging.INFO, "✅ Nhập username")
        time.sleep(3)  # Dừng 3 giây để quan sát

        # Nhập password
        password = driver.find_element(By.NAME, "password")
        password.send_keys("1234")
        log_message(logging.INFO, "✅ Nhập password")
        time.sleep(3)  # Dừng 3 giây để quan sát

        # Nhấn Enter để đăng nhập
        password.send_keys(Keys.RETURN)
        log_message(logging.INFO, "🚀 Gửi yêu cầu đăng nhập...")
        time.sleep(5)  # Dừng 5 giây để trang load

        # Kiểm tra kết quả đăng nhập
        if "dashboard" in driver.current_url or "home" in driver.current_url:
            log_message(logging.INFO, "🎉 Đăng nhập thành công!")
        else:
            log_message(logging.ERROR, "❌ Đăng nhập thất bại!")

    except Exception as e:
        log_message(logging.ERROR, f"⚠️ Lỗi khi chạy test: {e}")

    finally:
        time.sleep(3)  # Dừng 3 giây trước khi đóng trình duyệt
        driver.quit()
        log_message(logging.INFO, "🛑 Đã đóng trình duyệt")

# Hàm hiển thị kết quả test trên web
def test_results_view(request):
    return render(request, 'test_results.html', {'logs': TEST_LOGS})

# Chạy test khi file được gọi
if __name__ == "__main__":
    run_selenium_test()