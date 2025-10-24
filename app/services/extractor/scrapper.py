import asyncio
from typing import Iterable, Dict, Optional

from aiohttp import ClientSession, ClientTimeout
from playwright.async_api import async_playwright, TimeoutError as PWTimeout #type: ignore

from app.log.logger import logger


class AsyncFindChipsScraper:
    """Asynchronous scraper for FindChips using Playwright (Chromium)"""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        user_agent: Optional[str] = None,
        locale: str = "en-US",
        sleep_between: float = 1.0,
        nav_timeout_ms: int = 60_000,
        networkidle_timeout_ms: int = 30_000,
        headless: bool = True,
        max_concurrency: int = 15,
    ) -> None:
        self.headers = dict(self.DEFAULT_HEADERS)
        if user_agent:
            self.headers["User-Agent"] = user_agent

        self.locale = locale
        self.sleep_between = sleep_between
        self.nav_timeout_ms = nav_timeout_ms
        self.networkidle_timeout_ms = networkidle_timeout_ms
        self.headless = headless
        self.max_concurrency = max_concurrency

        # Lazy-initialized resources
        self._session: Optional[ClientSession] = None
        self._playwright = None
        self._browser = None
        self._context = None

    async def __aenter__(self):
        """Start browser and HTTP session"""
        self._session = ClientSession(timeout=ClientTimeout(total=20))
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless, args=["--no-sandbox"]
        )
        self._context = await self._browser.new_context(
            user_agent=self.headers["User-Agent"], locale=self.locale
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Gracefully close resources"""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        finally:
            if self._session and not self._session.closed:
                await self._session.close()

    async def _ensure_browser(self):
        """Ensure browser context is available (for non-context use)"""
        if not self._playwright:
            self._playwright = await async_playwright().start()
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless, args=["--no-sandbox"]
            )
        if not self._context:
            self._context = await self._browser.new_context(
                user_agent=self.headers["User-Agent"], locale=self.locale
            )

    async def get_rendered_html(self, url: str) -> Optional[str]:
        """Render a page using Playwright and return its full HTML"""
        await self._ensure_browser()
        try:
            page = await self._context.new_page()
            await page.goto(url, timeout=self.nav_timeout_ms)
            await page.wait_for_load_state("networkidle", timeout=self.networkidle_timeout_ms)
            await asyncio.sleep(self.sleep_between)
            html = await page.content()
            await page.close()
            logger.info(f"[WEBSCRAPING] Successfully rendered {url}.")
            return html
        except PWTimeout:
            logger.warning(f"[WEBSCRAPING] Timeout rendering {url}.")
        except Exception as e:
            logger.warning(f"[WEBSCRAPING] Error rendering {url}: {e}")
        return None

    async def fetch_part(self, part_number: str) -> Optional[str]:
        """Fetch and render a single part number from FindChips"""
        url = f"https://www.findchips.com/search/{part_number}"
        logger.info(f"[WEBSCRAPING] Fetching PN: {part_number} ({url})")
        html = await self.get_rendered_html(url)
        if not html:
            logger.warning(f"[WEBSCRAPING] Failed to fetch {part_number}. Skipping...")
            return None
        await asyncio.sleep(self.sleep_between)
        return html

    async def fetch_many(self, part_numbers: Iterable[str]) -> Dict[str, str]:
        """Fetch multiple part numbers concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrency)
        results: Dict[str, str] = {}

        async def worker(pn: str):
            async with semaphore:
                html = await self.fetch_part(pn)
                if html:
                    results[pn] = html

        await asyncio.gather(*(worker(pn) for pn in part_numbers))
        return results

    async def aclose(self):
        """Manually close resources (if not using async with)"""
        await self.__aexit__(None, None, None)
