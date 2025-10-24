# app/services/extractor/scrapper.py
import asyncio
from typing import Iterable, Dict, Optional

import aiohttp
from aiohttp import ClientTimeout
from playwright.async_api import async_playwright, TimeoutError as PWTimeout  # type: ignore

from app.log.logger import logger


class AsyncFindChipsScraper:

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
        requests_timeout: int = 20,
        nav_timeout_ms: int = 60_000,
        networkidle_timeout_ms: int = 30_000,
        headless: bool = True,
        max_concurrency: int = 4,
    ) -> None:
        self.headers = dict(self.DEFAULT_HEADERS)
        if user_agent:
            self.headers["User-Agent"] = user_agent

        self.locale = locale
        self.sleep_between = sleep_between
        self.requests_timeout = requests_timeout
        self.nav_timeout_ms = nav_timeout_ms
        self.networkidle_timeout_ms = networkidle_timeout_ms
        self.headless = headless
        self.max_concurrency = max_concurrency

        # Recursos lazy (inicializados em __aenter__)
        self._session: Optional[aiohttp.ClientSession] = None
        self._playwright = None
        self._browser = None
        self._context = None

    # Context manager assíncrono
    async def __aenter__(self):
        # Reutiliza uma sessão HTTP para todas as requisições do ciclo de vida do scraper
        self._session = aiohttp.ClientSession(timeout=ClientTimeout(total=self.requests_timeout))
        # Sobe o Playwright + Chromium uma vez
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless, args=["--no-sandbox"])
        self._context = await self._browser.new_context(
            user_agent=self.headers["User-Agent"],
            locale=self.locale,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
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

    # Inners Helpers
    @property
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            # Uso fora de `async with`: cria sessão on-demand
            self._session = aiohttp.ClientSession(timeout=ClientTimeout(total=self.requests_timeout))
        return self._session

    async def _ensure_browser(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(headless=self.headless, args=["--no-sandbox"])
        if not self._context:
            self._context = await self._browser.new_context(
                user_agent=self.headers["User-Agent"],
                locale=self.locale,
            )

    # Public Methods
    async def get_raw_html(self, url: str) -> Optional[str]:
        """Get the raw HTML (without JS) by aiohttp, não-bloqueante."""
        try:
            async with self.session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                return await resp.text()
        except Exception as e:
            logger.warning(f"[WEBSCRAPING] Error when getting RAW html for {url}: {e}")
            return None

    async def get_rendered_html(self, url: str) -> Optional[str]:
        """Renders the page on Chromium and returns the final HTML"""
        await self._ensure_browser()
        try:
            page = await self._context.new_page()
            await page.goto(url, timeout=self.nav_timeout_ms)
            await page.wait_for_load_state("networkidle", timeout=self.networkidle_timeout_ms)

            # Espaço para eventuais scripts dinâmicos carregarem (anti-flaky)
            await asyncio.sleep(self.sleep_between)

            html = await page.content()
            await page.close()

            logger.info(f"[WEBSCRAPING] Success to get rendered html from {url}.")
            return html
        except PWTimeout:
            logger.warning(f"[WEBSCRAPING] Timeout while rendering {url}.")
            return None
        except Exception as e:
            logger.warning(f"[WEBSCRAPING] Playwright error for {url}: {e}")
            return None

    @staticmethod
    def combine_html(raw_html: str, rendered_html: str) -> str:
        """Combina RAW + Rendered em um único HTML de referência (string)."""
        return (
            "<html><body>"
            f"<pre>{raw_html}</pre>"
            f"<pre>{rendered_html}</pre>"
            "</body></html>"
        )

    async def fetch_part(self, pn: str) -> Optional[str]:
        """Baixa e renderiza 1 PN (retorna o HTML combinado como string)."""
        url = f"https://www.findchips.com/search/{pn}"
        logger.info(f"[WEBSCRAPING] Start PN: {pn} ({url})")

        raw_html = await self.get_raw_html(url)
        if not raw_html:
            logger.warning(f"[WEBSCRAPING] Failed to get RAW html for PN {pn}. Skipping...")
            return None

        await asyncio.sleep(self.sleep_between)

        rendered_html = await self.get_rendered_html(url)
        if not rendered_html:
            logger.warning(f"[WEBSCRAPING] Failed to get RENDERED html for PN {pn}. Skipping...")
            return None

        await asyncio.sleep(self.sleep_between)
        return self.combine_html(raw_html, rendered_html)

    async def fetch_many(self, pns: Iterable[str]) -> Dict[str, str]:
        """
        Baixa vários PNs em paralelo, respeitando max_concurrency.
        Retorna dict {pn: combined_html}.
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)
        results: Dict[str, str] = {}

        async def _worker(pn: str):
            async with semaphore:
                html = await self.fetch_part(pn)
                if html:
                    results[pn] = html

        await asyncio.gather(*[_worker(pn) for pn in pns], return_exceptions=False)
        return results

    # Uso sem context manager (fecha tudo manualmente)
    async def aclose(self):
        """Fecha manualmente os recursos (se não usar `async with`)."""
        await self.__aexit__(None, None, None)
