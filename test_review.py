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
ERROR_IMG_DIR = "screenshots"
REPORT_DIR = "report"
REPORT_FILE = os.path.join(REPORT_DIR, "test_report.txt")

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(ERROR_IMG_DIR, exist_ok=True)


def write_report(test_name, status, message=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {test_name} - {status}\n"
    if message:
        error_summary = str(message).split("\n")[0]
        log_entry += f"  Message: {error_summary}\n"
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
        f.write("-" * 50 + "\n")


def login(driver, wait):
    driver.get(LOGIN_URL)
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Email']")
        )
    ).send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']").send_keys(
        PASSWORD
    )
    driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
    time.sleep(3)


def goto_review_tab(driver, wait):
    driver.get(LEARNING_URL)
    review_tab = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Đánh giá')]"))
    )
    review_tab.click()
    time.sleep(1)


def submit_review(driver, wait, review_text, star_index=4):
    review_input = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "textarea[placeholder*='Bạn nghĩ gì']")
        )
    )
    review_input.clear()
    review_input.send_keys(review_text)
    stars = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text-3xl"))
    )
    if len(stars) > star_index:
        driver.execute_script("arguments[0].click();", stars[star_index])
    send_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Gửi đánh giá')]")
        )
    )
    driver.execute_script("arguments[0].click();", send_btn)
    time.sleep(2)


def find_review_element(driver, wait, review_text):
    return wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[contains(., '{review_text}') and .//button[.//i[contains(@class,'fa-thumbs-up')]]]",
            )
        )
    )


def like_dislike_review(driver, wait, review_element):
    try:
        like_span_locator = (
            By.XPATH,
            ".//button[.//i[contains(@class,'fa-thumbs-up')]]/span",
        )
        like_btn = review_element.find_element(
            By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-up')]]"
        )
        like_count_span = review_element.find_element(*like_span_locator)
        old_like_count = int(like_count_span.text)
        like_btn.click()
        print("Đã like.")

        wait.until(
            EC.text_to_be_present_in_element(like_span_locator, str(old_like_count + 1))
        )
        new_like_count = int(review_element.find_element(*like_span_locator).text)
        assert new_like_count == old_like_count + 1, "Like không cập nhật ngay!"
        print("Like review cập nhật giao diện ngay!")

        dislike_span_locator = (
            By.XPATH,
            ".//button[.//i[contains(@class,'fa-thumbs-down')]]/span",
        )
        dislike_btn = review_element.find_element(
            By.XPATH, ".//button[.//i[contains(@class,'fa-thumbs-down')]]"
        )
        dislike_count_span = review_element.find_element(*dislike_span_locator)
        old_dislike_count = int(dislike_count_span.text)
        dislike_btn.click()
        print("Đã dislike.")

        wait.until(
            EC.text_to_be_present_in_element(
                dislike_span_locator, str(old_dislike_count + 1)
            )
        )
        new_dislike_count = int(review_element.find_element(*dislike_span_locator).text)
        assert new_dislike_count == old_dislike_count + 1, (
            "Dislike không cập nhật ngay!"
        )
        print("Dislike review cập nhật giao diện ngay!")
    except Exception as e:
        print(f"Lỗi khi Like/Dislike: {e}")
        raise


def test_review_valid(driver, wait):
    TEST_NAME = "Gửi review hợp lệ và Like/Dislike"
    try:
        review_text = "Review kiểm thử tự động hợp lệ!"
        submit_review(driver, wait, review_text, star_index=4)
        assert review_text in driver.page_source, "Review không xuất hiện!"
        review_element = find_review_element(driver, wait, review_text)
        like_dislike_review(driver, wait, review_element)
        print(f"{TEST_NAME}: Thành công")
        write_report(TEST_NAME, "THÀNH CÔNG")
    except Exception as e:
        print(f"{TEST_NAME}: Thất bại\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "THẤT BẠI", str(e))


def test_review_empty(driver, wait):
    TEST_NAME = "Gửi review rỗng"
    try:
        # Không nhập gì vào textarea, chỉ kiểm tra trạng thái nút gửi
        review_input = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "textarea[placeholder*='Bạn nghĩ gì']")
            )
        )
        review_input.clear()
        send_btn = driver.find_element(
            By.XPATH, "//button[contains(text(),'Gửi đánh giá')]"
        )
        # Nếu nút gửi bị disabled thì test thành công
        assert not send_btn.is_enabled(), "Nút gửi không bị disabled khi review rỗng!"
        print(f"{TEST_NAME}: Thành công")
        write_report(TEST_NAME, "THÀNH CÔNG")
    except Exception as e:
        print(f"{TEST_NAME}: Thất bại\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "THẤT BẠI", str(e))


def test_review_min_star(driver, wait):
    TEST_NAME = "Gửi review 1 sao"
    try:
        review_text = "Review kiểm thử 1 sao!"
        submit_review(driver, wait, review_text, star_index=0)
        assert review_text in driver.page_source, "Review không xuất hiện!"
        print(f"{TEST_NAME}: Thành công")
        write_report(TEST_NAME, "THÀNH CÔNG")
    except Exception as e:
        print(f"{TEST_NAME}: Thất bại\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "THẤT BẠI", str(e))


def test_review_reply(driver, wait):
    TEST_NAME = "Phản hồi review"
    try:
        review_text = "Review kiểm thử phản hồi!"
        submit_review(driver, wait, review_text, star_index=3)
        review_element = find_review_element(driver, wait, review_text)
        reply_btn = review_element.find_element(
            By.XPATH, ".//button[contains(text(),'Phản hồi')]"
        )
        reply_btn.click()
        time.sleep(1)
        reply_input = review_element.find_element(By.CSS_SELECTOR, "textarea")
        reply_input.send_keys("Đây là phản hồi tự động!")
        send_reply_btn = review_element.find_element(
            By.XPATH, "//button[contains(text(),'Gửi')]"
        )
        send_reply_btn.click()
        time.sleep(2)
        assert "Đây là phản hồi tự động!" in driver.page_source, (
            "Phản hồi không xuất hiện!"
        )
        print(f"{TEST_NAME}: Thành công")
        write_report(TEST_NAME, "THÀNH CÔNG")
    except Exception as e:
        print(f"{TEST_NAME}: Thất bại\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "THẤT BẠI", str(e))


if __name__ == "__main__":
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    try:
        login(driver, wait)
        # Các test case chỉ thực hiện thao tác review, KHÔNG gọi lại login
        goto_review_tab(driver, wait)
        test_review_valid(driver, wait)
        test_review_empty(driver, wait)
        test_review_min_star(driver, wait)
        test_review_reply(driver, wait)
    finally:
        print("Đóng trình duyệt sau 5 giây.")
        time.sleep(5)
        driver.quit()
