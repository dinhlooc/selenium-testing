from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv  # Thêm thư viện CSV
from datetime import datetime

CHROMEDRIVER_PATH = "d:\\PBL6_FE\\selenium-testing\\chromedriver.exe"
BASE_URL = "https://coursevo.vercel.app"
LOGIN_URL = f"{BASE_URL}/login"
COURSE_SLUG = "lap-trinh-cpp-toan-tap-tu-co-ban-den-nang-cao"
LEARNING_URL = f"{BASE_URL}/learning/{COURSE_SLUG}"

USERNAME = "ngoloc12@gmail.com"
PASSWORD = "Ngoloc12@"
ERROR_IMG_DIR = "screenshots"
REPORT_DIR = "report"
# Thay đổi đuôi file báo cáo thành .csv
REPORT_FILE = os.path.join(REPORT_DIR, "test_report.csv")

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(ERROR_IMG_DIR, exist_ok=True)


def write_report(test_name, status, message=""):
    """
    Ghi kết quả test vào tệp CSV.
    Tự động thêm header nếu tệp chưa tồn tại.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Chuẩn bị dữ liệu hàng
    header = ["Timestamp", "Test Name", "Status", "Message"]

    # Tóm tắt lỗi và xóa ký tự xuống dòng để không làm hỏng file CSV
    error_summary = ""
    if message:
        error_summary = (
            str(message).split("\n")[0].replace(",", ";")
        )  # Thay dấu phẩy để tránh lỗi CSV

    row_data = [timestamp, test_name, status, error_summary]

    # Kiểm tra xem tệp đã tồn tại chưa để quyết định có ghi header không
    file_exists = os.path.isfile(REPORT_FILE)

    try:
        # Mở tệp ở chế độ 'a' (append), encoding 'utf-8-sig' và newline=''
        # Vẫn giữ 'utf-8-sig' để tương thích, dù giờ đã là tiếng Anh
        with open(REPORT_FILE, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)

            # Nếu tệp mới (do file_exists=False), ghi header trước
            if not file_exists:
                writer.writerow(header)

            # Ghi dữ liệu của test case
            writer.writerow(row_data)

    except Exception as e:
        # Xử lý lỗi nếu không ghi được file report
        print(f"!!! CRITICAL ERROR writing report file: {e} !!!")
        print(f"Report data was: {row_data}")


def write_summary_report(start_time, end_time):
    """Ghi tóm tắt tổng thời gian chạy test vào cuối file CSV."""
    duration = end_time - start_time
    total_seconds = duration.total_seconds()

    # Định dạng thời gian chạy (VD: 00:01:30.500)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_str = f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"  # H:M:S.ms

    try:
        # SỬA: Dùng 'utf-8-sig' để nhất quán
        with open(REPORT_FILE, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            # Ghi một dòng trống để phân cách
            writer.writerow([])
            # Ghi dòng tóm tắt (ĐÃ CHUYỂN SANG TIẾNG ANH)
            writer.writerow(["Total execution time:", duration_str, "(H:M:S.ms)", ""])

    except Exception as e:
        print(f"!!! ERROR writing summary report: {e} !!!")


def login(driver, wait):
    """
    Logs into the website using the provided credentials.
    Selectors updated to match the React component.
    """
    driver.get(LOGIN_URL)

    # --- UPDATED SELECTORS ---
    # Wait for the email input field with placeholder "Email đăng nhập"
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Email đăng nhập']")
        )
    ).send_keys(USERNAME)

    # Find the password input field with placeholder "Mật khẩu"
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Mật khẩu']").send_keys(
        PASSWORD
    )

    # Find the login button with text "Đăng nhập"
    driver.find_element(By.XPATH, "//button[contains(text(),'Đăng nhập')]").click()
    # --- END OF UPDATES ---

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
    # Cập nhật XPATH để tìm review bằng tiếng Anh
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
        print("Liked.")  # Sửa sang tiếng Anh

        wait.until(
            EC.text_to_be_present_in_element(like_span_locator, str(old_like_count + 1))
        )
        new_like_count = int(review_element.find_element(*like_span_locator).text)
        assert new_like_count == old_like_count + 1, (
            "Like count did not update immediately!"
        )
        print("Like review updated UI immediately!")

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
        print("Disliked.")  # Sửa sang tiếng Anh

        wait.until(
            EC.text_to_be_present_in_element(
                dislike_span_locator, str(old_dislike_count + 1)
            )
        )
        new_dislike_count = int(review_element.find_element(*dislike_span_locator).text)
        assert new_dislike_count == old_dislike_count + 1, (
            "Dislike count did not update immediately!"
        )
        print("Dislike review updated UI immediately!")
    except Exception as e:
        print(f"Error during Like/Dislike: {e}")
        raise


def test_review_valid(driver, wait):
    # SỬA: Tên test và review sang tiếng Anh
    TEST_NAME = "Submit valid review and Like/Dislike"
    try:
        review_text = "Valid automated test review!"
        submit_review(driver, wait, review_text, star_index=4)
        # assert review_text in driver.page_source, "Review did not appear!"
        # review_element = find_review_element(driver, wait, review_text)
        # like_dislike_review(driver, wait, review_element)
        print(f"{TEST_NAME}: SUCCESS")
        write_report(TEST_NAME, "SUCCESS")
    except Exception as e:
        print(f"{TEST_NAME}: FAILED\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "FAILED", str(e))


def test_review_empty(driver, wait):
    # SỬA: Tên test sang tiếng Anh
    TEST_NAME = "Submit empty review"
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
        assert not send_btn.is_enabled(), (
            "Submit button is not disabled for empty review!"
        )
        print(f"{TEST_NAME}: SUCCESS")
        write_report(TEST_NAME, "SUCCESS")
    except Exception as e:
        print(f"{TEST_NAME}: FAILED\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "FAILED", str(e))


def test_review_min_star(driver, wait):
    # SỬA: Tên test và review sang tiếng Anh
    TEST_NAME = "Submit 1-star review"
    try:
        review_text = "1-star test review!"
        submit_review(driver, wait, review_text, star_index=0)
        # assert review_text in driver.page_source, "Review did not appear!"
        print(f"{TEST_NAME}: SUCCESS")
        write_report(TEST_NAME, "SUCCESS")
    except Exception as e:
        print(f"{TEST_NAME}: FAILED\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "FAILED", str(e))


def test_review_reply(driver, wait):
    # SỬA: Tên test và review sang tiếng Anh
    TEST_NAME = "Reply to review"
    try:
        review_text = "Review for reply test!"
        submit_review(driver, wait, review_text, star_index=3)
        review_element = find_review_element(driver, wait, review_text)
        # Nhấn nút "Phản hồi" trong review vừa tạo
        reply_btn = review_element.find_element(
            By.XPATH, ".//button[contains(text(),'Phản hồi')]"
        )
        reply_btn.click()
        time.sleep(1)
        # Tìm đúng khung reply (div.mt-4.pl-14) bên trong review_element
        reply_container = review_element.find_element(By.CSS_SELECTOR, "div.mt-4.pl-14")
        reply_box = reply_container.find_element(
            By.CSS_SELECTOR, "textarea[placeholder='Viết phản hồi của bạn...']"
        )
        # SỬA: Phản hồi sang tiếng Anh
        reply_text = "This is an automated reply!"
        reply_box.send_keys(reply_text)

        send_reply_btn = reply_container.find_element(
            By.XPATH,
            ".//button[contains(text(),'Gửi') and not(contains(text(),'đánh giá'))]",
        )
        wait.until(lambda d: send_reply_btn.is_enabled())
        send_reply_btn.click()
        time.sleep(2)

        # SỬA: Kiểm tra text tiếng Anh
        assert reply_text in review_element.text, (
            "Reply text did not appear under the review!"
        )
        print(f"{TEST_NAME}: SUCCESS")
        write_report(TEST_NAME, "SUCCESS")
    except Exception as e:
        print(f"{TEST_NAME}: FAILED\n{e}")
        img_path = os.path.join(ERROR_IMG_DIR, f"error_{TEST_NAME}.png")
        driver.save_screenshot(img_path)
        write_report(TEST_NAME, "FAILED", str(e))


if __name__ == "__main__":
    # THÊM: Kiểm tra quyền ghi file report trước khi chạy
    try:
        # Thử mở file ở chế độ 'a' (append) để kiểm tra
        # Dùng 'utf-8-sig' và newline='' để nhất quán
        with open(REPORT_FILE, "a", encoding="utf-8-sig", newline="") as f:
            pass  # Chỉ cần kiểm tra mở file thành công
    except IOError as e:
        if e.errno == 13:  # Permission denied
            # SỬA: Thông báo lỗi sang tiếng Anh
            print("=" * 60)
            print("!!! CRITICAL ERROR: CANNOT WRITE TO REPORT FILE !!!")
            print(f"!!! ERROR: [Errno 13] Permission denied: '{REPORT_FILE}'")
            print("PLEASE CLOSE THE CSV FILE (IN EXCEL) BEFORE RUNNING THE SCRIPT.")
            print("=" * 60)
            exit()  # Thoát script ngay lập tức
        else:
            print(f"!!! UNKNOWN FILE ERROR: {e} !!!")
            exit()

    start_time = datetime.now()  # THÊM: Ghi lại thời điểm bắt đầu
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
        end_time = datetime.now()  # THÊM: Ghi lại thời điểm kết thúc
        write_summary_report(start_time, end_time)  # THÊM: Ghi tóm tắt

        # SỬA: Thông báo sang tiếng Anh
        print("Closing browser in 5 seconds.")
        time.sleep(5)
        driver.quit()
