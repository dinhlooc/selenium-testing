from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

CHROMEDRIVER_PATH = "d:\\PBL6_FE\\selenium-testing\\chromedriver.exe"
BASE_URL = "http://localhost:3000"
LOGIN_URL = f"{BASE_URL}/login"
COURSE_SLUG = "lap-trinh-cpp-toan-tap-tu-co-ban-den-nang-cao"
LEARNING_URL = f"{BASE_URL}/learning/{COURSE_SLUG}" 

USERNAME = "ngoloc12@gmail.com"
PASSWORD = "Ngoloc12@"
REVIEW_TEXT = "Review kiểm thử tự động bằng Selenium!"

TEST_NAME = "Review Submission and Interaction"
REPORT_DIR = "report"
REPORT_FILE = os.path.join(REPORT_DIR, "test_report.txt")
ERROR_IMG_DIR = "screenshots"

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(ERROR_IMG_DIR, exist_ok=True)

def write_report(status, message=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {TEST_NAME} - {status}\n"
    if message:
        # Tóm tắt thông báo lỗi cho gọn
        error_summary = str(message).split('\n')[0]
        log_entry += f"  Message: {error_summary}\n"
    
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
        f.write("-" * 50 + "\n")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

try:
    print("Bắt đầu đăng nhập...")
    driver.get(LOGIN_URL)

    print("Đang tìm ô email...")
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input[placeholder='Email']")
    )).send_keys(USERNAME)

    print("Đang tìm ô password...")
    driver.find_element(
        By.CSS_SELECTOR, "input[placeholder='Password']"
    ).send_keys(PASSWORD)

    print("Đang nhấn nút Login...")
    driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

    print("Đang chờ đăng nhập thành công...")
    time.sleep(5) 

    print(f"Truy cập trang learning: {LEARNING_URL}")
    driver.get(LEARNING_URL)

    print("Đang mở tab 'Đánh giá'...")
    review_tab = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(),'Đánh giá')]")
    ))
    review_tab.click()
    
    time.sleep(1) 

    print("Đang chờ ô review...")
    review_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Bạn nghĩ gì']")))
    review_input.send_keys(REVIEW_TEXT)
    print("Đã nhập review.")

    print("Đang chọn 5 sao...")
    stars = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text-3xl")))
    if len(stars) >= 5:
        driver.execute_script("arguments[0].click();", stars[4])
    print("Đã chọn sao.")

    print("Đang gửi review...")
    send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Gửi đánh giá')]")))
    driver.execute_script("arguments[0].click();", send_btn)

    print("Đang chờ review xuất hiện...")
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), REVIEW_TEXT))
    print("Gửi review thành công!")
    
    print("Chờ 2 giây để UI review ổn định...")
    time.sleep(2) 

    print("Bắt đầu Like/Dislike...")

    try:
        review_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, f"//*[contains(., '{REVIEW_TEXT}') and .//button[.//i[contains(@class,'fa-thumbs-up')]]]")
        ))
    except Exception as e:
        print(f"Không thể tìm thấy container của review: {e}")
        raise Exception("Không tìm thấy review vừa gửi để Like/Dislike!")

    like_span_locator = (By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-up')]]/span")
    
    like_btn = review_element.find_element(By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-up')]]")
    like_count_span = review_element.find_element(*like_span_locator) 
    old_like_count = int(like_count_span.text)
    like_btn.click()
    print("Đã like.")

    wait.until(EC.text_to_be_present_in_element(like_span_locator, str(old_like_count + 1)))
    
    new_like_count = int(review_element.find_element(*like_span_locator).text)
    assert new_like_count == old_like_count + 1, "Like không cập nhật ngay!"
    print("Like review cập nhật giao diện ngay!")

    dislike_span_locator = (By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-down')]]/span")

    dislike_btn = review_element.find_element(By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-down')]]")
    dislike_count_span = review_element.find_element(*dislike_span_locator)
    old_dislike_count = int(dislike_count_span.text)
    dislike_btn.click()
    print("Đã dislike.")

    wait.until(EC.text_to_be_present_in_element(dislike_span_locator, str(old_dislike_count + 1)))
    
    new_dislike_count = int(review_element.find_element(*dislike_span_locator).text)
    assert new_dislike_count == old_dislike_count + 1, "Dislike không cập nhật ngay!"
    print("Dislike review cập nhật giao diện ngay!")

    print("\n--- TEST THÀNH CÔNG ---")
    write_report("THÀNH CÔNG")

except Exception as e:
    print(f"\n--- TEST THẤT BẠI ---")
    print(e)
    img_path = os.path.join(ERROR_IMG_DIR, "error_screenshot.png")
    driver.save_screenshot(img_path)
    print(f"Đã chụp ảnh lỗi '{img_path}'")
    write_report("THẤT BẠI", str(e))

finally:
    print("Đóng trình duyệt sau 5 giây.")
    time.sleep(5)
    driver.quit()