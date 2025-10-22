import time
import requests
from app.log.logger import logger
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout #type: ignore

# Headers to simulate a browser request and avoid blocking (without this, not all information from the site is extracted).
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36",
"Accept-Language": "en-US,en;q=0.9"}
DEFAULT_SLEEP_BETWEEN_REQUESTS = 1.0
REQUESTS_TIMEOUT = 20

def get_raw_html_from_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUESTS_TIMEOUT)
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        print(f"Error when try get the html to {url}: {e}")
        return None

def get_rendered_html_from_url(url):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(user_agent=HEADERS["User-Agent"], locale="en-US")
            page = context.new_page()

            page.goto(url, timeout=60_000)
            page.wait_for_load_state("networkidle", timeout=30_000)

            time.sleep(1.5)

            rendered = page.content()
            page.close()
            context.close()
            browser.close()

            return rendered
        except PWTimeout:
            print(f"Error: the page {url} took a long time to renderize .")
            return None

def get_combined_html(raw_html, rendered_html):
    combined_html_content = f"""
    <html>
    <body>
        <pre>{raw_html}</pre>
        <pre>{rendered_html}</pre>
    </body>
    </html>
    """
    return combined_html_content

def process_pn(pn, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS):
    url = f"https://www.findchips.com/search/{pn}"
    print(f"\Start the process PN: {pn}...")

    raw_html = get_raw_html_from_url(url)
    if not raw_html:
        print(f"Error to get html from {pn}. Skipping...")
        return None

    time.sleep(sleep_between)

    rendered_html = get_rendered_html_from_url(url)
    if not rendered_html:
        print(f"Error to get rederized html to PN {pn}. Skipping...")
        return None

    time.sleep(sleep_between)

    combined_html = get_combined_html(raw_html, rendered_html)
    return combined_html

def main():
    pns = ["NACE100M100V6.3X8TR13F", "1N4148W-TP"]


    print(f"Starting process of {len(pns)} PNs.")

    html_results = {}
    for pn in pns:
        html_content = process_pn(pn, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS)
        if html_content:
            html_results[pn] = html_content

    return html_results

if __name__ == "__main__":
    results = main()
    print(results.keys())
