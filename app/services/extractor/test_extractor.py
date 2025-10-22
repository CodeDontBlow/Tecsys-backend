import asyncio
import aiohttp
from .extractor import extract_from_html
from .scrapper import async_process_pn, DEFAULT_SLEEP_BETWEEN_REQUESTS

pns = {
    "01": "CL10C330JB8NNNC",
    "02": "CL10B472KB8NNNC",
    "03": "GRM1885C1H180JA01D", 
    "04": "CL10A106KP8NNNC",
    "05": "C1608X5R1E106M080AC",
    "06": "88512006119",
    "07": "NACE100M100V6.3X8TR13F",
    "08": "CRCW060320K0FKEA",
}

async def main():
    html_results = {}
    

    semaphore = asyncio.Semaphore(4)  
    
    async def fetch_pn_with_limit(pn, session):
        async with semaphore:
            html_content = await async_process_pn(pn, session, DEFAULT_SLEEP_BETWEEN_REQUESTS)
            return pn, html_content
    

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_pn_with_limit(pn, session) for pn in pns.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Error processing PN: {result}")
                continue
            pn, html_content = result
            if html_content:
                html_results[pn] = html_content

    target_supplier = 'Avnet'
    
    for html in html_results.values():
        result = extract_from_html(html, target_supplier)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())