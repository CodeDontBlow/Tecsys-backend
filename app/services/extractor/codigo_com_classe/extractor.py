import asyncio
import json
import re
from typing import Iterable, Dict, Optional

import aiohttp
from aiohttp import ClientTimeout
from playwright.async_api import async_playwright, TimeoutError as PWTimeout  # type: ignore
from bs4 import BeautifulSoup

from app.log.logger import logger


# SCRAPER ASSÍNCRONO (INTEGRADO)
class AsyncFindChipsScraper:
    """Class to fetch rendered HTML from Findchips asynchronously."""

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

        self._session: Optional[aiohttp.ClientSession] = None
        self._playwright = None
        self._browser = None
        self._context = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=ClientTimeout(total=self.requests_timeout))
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless, args=["--no-sandbox"])
        self._context = await self._browser.new_context(
            user_agent=self.headers["User-Agent"], locale=self.locale
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

    async def get_raw_html(self, url: str) -> Optional[str]:
        try:
            async with self._session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                return await resp.text()
        except Exception as e:
            logger.warning(f"[WEBSCRAPING] Error when getting RAW html for {url}: {e}")
            return None

    async def get_rendered_html(self, url: str) -> Optional[str]:
        try:
            page = await self._context.new_page()
            await page.goto(url, timeout=self.nav_timeout_ms)
            await page.wait_for_load_state("networkidle", timeout=self.networkidle_timeout_ms)
            await asyncio.sleep(self.sleep_between)
            html = await page.content()
            await page.close()
            return html
        except PWTimeout:
            logger.warning(f"[WEBSCRAPING] Timeout while rendering {url}.")
            return None
        except Exception as e:
            logger.warning(f"[WEBSCRAPING] Playwright error for {url}: {e}")
            return None

    async def fetch_part(self, pn: str) -> Optional[str]:
        """Return combined HTML (raw + rendered) for one part number."""
        url = f"https://www.findchips.com/search/{pn}"
        logger.info(f"[WEBSCRAPING] Fetching {pn} ({url})")

        raw_html = await self.get_raw_html(url)
        if not raw_html:
            return None
        await asyncio.sleep(self.sleep_between)

        rendered_html = await self.get_rendered_html(url)
        if not rendered_html:
            return None
        await asyncio.sleep(self.sleep_between)

        return f"<html><body><pre>{raw_html}</pre><pre>{rendered_html}</pre></body></html>"

    async def fetch_many(self, pns: Iterable[str]) -> Dict[str, str]:
        """Fetch multiple part numbers concurrently."""
        semaphore = asyncio.Semaphore(self.max_concurrency)
        results: Dict[str, str] = {}

        async def worker(pn: str):
            async with semaphore:
                html = await self.fetch_part(pn)
                if html:
                    results[pn] = html

        await asyncio.gather(*[worker(pn) for pn in pns])
        return results


# EXTRACTOR
def clean_description(raw_description: str) -> str:
    """Clean messy description text from supplier data."""
    if "|" in raw_description:
        cleaned = raw_description.split("|")[0].strip()
    else:
        cleaned = raw_description

    patterns_to_remove = [
        r"RoHS:.*",
        r"RoHS Compliant:.*",
        r"Min Qty:.*",
        r"Package Multiple:.*",
        r"Date Code:.*",
        r"Container:.*",
        r"Part Details.*",
        r"\bYes$",
        r"\bNo$",
    ]

    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned)

    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.rstrip(" ,|")

    return cleaned if cleaned else "N/A"


def extract_from_html(html: str, target_supplier: str) -> str:
    """Extract structured data (JSON) from rendered Findchips HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # --- supplier name ---
    suppliers = [h3.get_text(strip=True) for h3 in soup.find_all("h3")]
    valid_suppliers = [s for s in suppliers if "Most Popular" not in s]

    found_supplier = None
    if target_supplier:
        for s in valid_suppliers:
            if target_supplier.lower() in s.lower():
                found_supplier = s
                break
    if not found_supplier:
        found_supplier = target_supplier or (valid_suppliers[0] if valid_suppliers else "Unknown")

    # --- disti number ---
    disti_number = "N/A"
    for span in soup.find_all("span", class_=re.compile(r"additional-title"), string=re.compile(r"DISTI\s*#")):
        parent = span.parent
        if parent:
            value_span = parent.find("span", class_=re.compile(r"additional-value"))
            if value_span:
                candidate = value_span.get_text(strip=True)
                if re.fullmatch(r"[A-Za-z0-9\-_.]{2,30}", candidate):
                    disti_number = candidate
                    break

    # --- main table ---
    table = soup.find("table")
    if not table:
        return json.dumps({"error": "Main table not found"}, indent=4, ensure_ascii=False)

    product_part_number = table.find("a")
    product_part_number = product_part_number.get_text(strip=True) if product_part_number else "N/A"

    rows = table.find_all("tr")
    if len(rows) > 1:
        columns = rows[1].find_all("td")
        manufacturer = columns[1].get_text(strip=True) if len(columns) > 1 else "N/A"
        raw_description = columns[2].get_text(strip=True) if len(columns) > 2 else "N/A"
        description = clean_description(raw_description)
    else:
        manufacturer = description = "N/A"

    data = {
        "supplier": found_supplier or "Unknown",
        "product_part_number": product_part_number,
        "part_number_supplier": disti_number,
        "manufacturer": manufacturer,
        "description": description,
    }

    logger.info(f"[WEBSCRAPING-EXTRACT] Successfully extracted from {data['product_part_number']}")
    return json.dumps(data, indent=4, ensure_ascii=False)


# TEST
async def main():
    pns = [
        "CL10C330JB8NNNC",
        "CL10B472KB8NNNC",
        "GRM1885C1H180JA01D",
        "CL10A106KP8NNNC",
        "C1608X5R1E106M080AC",
        "88512006119",
        "NACE100M100V6.3X8TR13F",
        "CRCW060320K0FKEA",
    ]
    target_supplier = "Avnet"

    async with AsyncFindChipsScraper(max_concurrency=4) as scraper:
        html_by_pn = await scraper.fetch_many(pns)

    for pn, html in html_by_pn.items():
        print(extract_from_html(html, target_supplier))


if __name__ == "__main__":
    asyncio.run(main())
