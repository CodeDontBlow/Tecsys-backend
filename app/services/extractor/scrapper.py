import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout  # type: ignore

class FindChipsScraper:
    """Class that retrieves the rendered HTML content from Findchips pages"""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, sleep_between: float = 1.0, timeout: int = 60_000):
        self.sleep_between = sleep_between
        self.timeout = timeout

    def get_rendered_html(self, url: str) -> str | None:
        """Renders the page in Chromium and returns the full HTML as a string."""
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(user_agent=self.HEADERS["User-Agent"], locale="en-US")
                page = context.new_page()

                page.goto(url, timeout=self.timeout)
                page.wait_for_load_state("networkidle", timeout=30_000)

                time.sleep(self.sleep_between)

                html = page.content()

                page.close()
                context.close()
                browser.close()

                return html

            except PWTimeout:
                print(f"[ERROR] Requested timed out for {url}.")
                return None

    def get_html(self, part_number: str) -> str | None:
        """Receives a part number, accesses the website and returns the rendered HTML."""
        url = f"https://www.findchips.com/search/{part_number}"
        print(f"[INFO] Accessing {url}...")
        html = self.get_rendered_html(url)
        if not html:
            print(f"[ERROR] Failed to capture HTML for {part_number}.")
            return None
        return html
