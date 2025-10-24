from .extractor import extract_from_html
from .scrapper import AsyncFindChipsScraper
import json


async def webscraping(pns, supplier):
    results = []
    async with AsyncFindChipsScraper() as scraper:
        html_by_pn = await scraper.fetch_many(pns)

    for pn, html in html_by_pn.items():
        data = extract_from_html(html, supplier)

        # Se vier string, tenta converter para dict
        if isinstance(data, str):
            data = data.strip()  # remove espaços em branco
            if data:  # se não estiver vazia
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    print(f"⚠️ JSON inválido para PN {pn}: {data}")
                    data = {}  # ou algum dict padrão
            else:
                data = {}  # string vazia vira dict vazio

        results.append(data)
    return results