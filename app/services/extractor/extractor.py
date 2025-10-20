from bs4 import BeautifulSoup
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parents[3]
SCRAPER_RESULTS_DIR = BASE_DIR / "app" / "services"/ "extractor" / "web-scraping" / "scraper_results"


def get_latest_scrape_dir(base_dir: Path) -> Path:
    """Retorna o diretório mais recente dentro de scraper_results/"""
    scrape_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("scrape_")]
    if not scrape_dirs:
        raise FileNotFoundError("Nenhum diretório 'scrape_' encontrado em scraper_results/")
    return max(scrape_dirs, key=lambda d: d.stat().st_mtime)


def extract_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Extrair fornecedor (primeiro h3 válido)
    supplier_tag = soup.find("h3")
    supplier = supplier_tag.get_text(strip=True) if supplier_tag else "Desconhecido"
    if "Most Popular" in supplier:
        supplier = "Desconhecido"

    # Extrair part number principal
    product_part = soup.find("a")
    product_part_number = product_part.get_text(strip=True) if product_part else "N/A"

    # Procurar o DISTI #
    disti_number = None
    for tag in soup.find_all(["div", "td", "span"]):
        text = tag.get_text(" ", strip=True)
        if "DISTI #" in text:
            match = text.split("DISTI #")[-1].strip()
            if match:
                disti_number = match
                break
    if not disti_number:
        disti_number = "N/A"

    # Fabricante e descrição
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            cols = rows[1].find_all("td")
            manufacturer = cols[1].get_text(strip=True) if len(cols) > 1 else "N/A"
            description = cols[2].get_text(strip=True) if len(cols) > 2 else "N/A"
        else:
            manufacturer = description = "N/A"
    else:
        manufacturer = description = "N/A"

    return {
        "supplier": supplier,
        "product_part_number": product_part_number,
        "part_number_fornecedor": disti_number,
        "manufacturer": manufacturer,
        "description": description,
    }


if __name__ == "__main__":

    latest_scrape_dir = get_latest_scrape_dir(SCRAPER_RESULTS_DIR)
    html_file = latest_scrape_dir / "NACE100M100V6.3X8TR13F.html"
    result = extract_from_html(html_file)
    print(result)
