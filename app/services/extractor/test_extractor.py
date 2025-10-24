import asyncio
from playwright.async_api import async_playwright, TimeoutError as PWTimeout  # type: ignore


from app.log.logger import logger
from .extractor import extract_from_html
from .scrapper import AsyncFindChipsScraper

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

    async with AsyncFindChipsScraper() as scraper:
        html_by_pn = await scraper.fetch_many(pns)

    for pns, html in html_by_pn.items():
        print(extract_from_html(html, target_supplier))


if __name__ == "__main__":
    asyncio.run(main())