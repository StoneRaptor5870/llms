import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import ollama

MODEL = 'llama3.2:1b'

class WebsiteCrawler: 
    def __init__(self, url, wait_time=20, chrome_binary_path=None):
        """
        Initialize the website crawler using selenium to scrape content.
        """
        self.url = url
        self.wait_time = wait_time

        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        )

        if chrome_binary_path:
            options.binary_location = chrome_binary_path

        self.driver = uc.Chrome(options=options)

        try:
            # load the URL
            self.driver.get(url)

            # wait for cloudflare or similar checks
            time.sleep(10)

            # ensure main content is loaded
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )

            # extract the content
            main_content = self.driver.find_element(By.CSS_SELECTOR, "main").get_attribute("outerHTML")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(main_content, "html.parser")
            self.title = self.driver.title if self.driver.title else "No title found"
            self.text = soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"Error occurred: {e}")
            self.title = "Error occurred"
            self.text = ""

        finally:
            self.driver.quit()

def summarize_content(web_crawler):
    """
    Send the scraped content to Ollama for summarization.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant summarizing web content."},
        {"role": "user", "content": f"Title: {web_crawler.title}\n\nContent: {web_crawler.text}"}
    ]

    response = ollama.chat(model=MODEL, messages=messages)
    return response.get("message", {}).get("content", "No summary available")

chrome_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
url = "https://www.anthropic.com/"
crawler = WebsiteCrawler(url, chrome_binary_path=chrome_path)
summary = summarize_content(crawler)

print(summary)