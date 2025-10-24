import asyncio
import aiohttp
from app.log.logger import logger
from playwright.async_api import async_playwright, TimeoutError as PWTimeout #type: ignore

# Headers to simulate a browser request and avoid blocking (without this, not all information from the site is extracted).
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36",
"Accept-Language": "en-US,en;q=0.9"}
DEFAULT_SLEEP_BETWEEN_REQUESTS = 1.0
REQUESTS_TIMEOUT = 20

async def async_get_raw_html_from_url(url, session):
    try:
        async with session.get(url, headers=HEADERS, timeout=REQUESTS_TIMEOUT) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.warning(f"[WEBSCRAPING] Error when try get the html to {url}: {e}")
        return None

async def async_get_rendered_html_from_url(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(user_agent=HEADERS["User-Agent"], locale="en-US")
            page = await context.new_page()

            await page.goto(url, timeout=60_000)
            await page.wait_for_load_state("networkidle", timeout=30_000)

            await asyncio.sleep(1.5)

            rendered = await page.content()
            await page.close()
            await context.close()
            await browser.close()

            logger.info(f"[WEBSCRAPING] Succes to get renderized html from {url}.")
            return rendered
    except PWTimeout:
        logger.warning(f"[WEBSCRAPING] Error: the page {url} took a long time to renderize.")
        return None
    except Exception as e:
        logger.warning(f"[WEBSCRAPING] Error in playwright for {url}: {e}")
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

async def async_process_pn(pn, session=None, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS):
    url = f"https://www.findchips.com/search/{pn}"
    logger.info(f"[WEBSCRAPING] Start the process PN: {pn}...")


    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        raw_html = await async_get_raw_html_from_url(url, session)
        if not raw_html:
            logger.warning(f"[WEBSCRAPING] Error to get html from {pn}. Skipping...")
            return None

        await asyncio.sleep(sleep_between)

        rendered_html = await async_get_rendered_html_from_url(url)
        if not rendered_html:
            logger.warning(f"[WEBSCRAPING] Error to get rederized html to PN {pn}. Skipping...")
            return None

        await asyncio.sleep(sleep_between)

        combined_html = get_combined_html(raw_html, rendered_html)
        return combined_html
    finally:
        if close_session and session:
            await session.close()

