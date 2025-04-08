import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_form_upload():
    # Set up headless Chrome for containerized execution
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("http://video-proc:5000/")
        time.sleep(1)

        # Fill in form
        title_input = driver.find_element(By.NAME, "title")
        file_input = driver.find_element(By.NAME, "file")

        # Create a dummy video file
        sample_path = "/tmp/sample.mp4"
        with open(sample_path, "wb") as f:
            f.write(b"FAKE MP4 CONTENT")

        title_input.send_keys("Selenium Test Upload")
        file_input.send_keys(sample_path)

        # Submit form
        form = driver.find_element(By.TAG_NAME, "form")
        form.submit()

        # Wait for redirect and processing
        time.sleep(3)

        # Verify video appears in list view
        assert "Video List" in driver.page_source
        assert "Selenium Test Upload" in driver.page_source

    finally:
        driver.quit()
