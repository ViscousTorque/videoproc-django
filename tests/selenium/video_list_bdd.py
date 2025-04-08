import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_video_list_page():
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("http://video-proc:5000/videos/")
        time.sleep(2)  # Wait for page to fully render

        assert "Video List" in driver.page_source

        video_items = driver.find_elements(By.TAG_NAME, "li")
        assert len(video_items) > 0, "No videos found on the page."

    finally:
        driver.quit()
