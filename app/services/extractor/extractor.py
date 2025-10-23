from bs4 import BeautifulSoup
from scrapper import FindChipsScraper
import re

def extract_findchips(part_number, target_supplier):
    scraper = FindChipsScraper()
    html = scraper.get_html(part_number)
    if not html:
        return {"erro": f"It's not possible to get HTML for {part_number}"}

    soup = BeautifulSoup(html, "html.parser")

    # Extract suppliers
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

    # Extract DISTI #
    disti_number = None

    #Search for all blocks that have the text "DISTI #"
    for span in soup.find_all("span", class_=re.compile(r"additional-title"), string=re.compile(r"DISTI\s*#")):
        parent = span.parent
        if parent:
            value_span = parent.find("span", class_=re.compile(r"additional-value"))
            if value_span:
                candidate = value_span.get_text(strip=True)
                if re.fullmatch(r"[A-Za-z0-9\-_.]{2,30}", candidate):
                    disti_number = candidate
                    break

    disti_number = disti_number or "N/A"


    # Extract main table
    table = soup.find("table")
    if not table:
        return {"erro": "Main table not found"}

    product_part_number = table.find("a")
    product_part_number = product_part_number.get_text(strip=True) if product_part_number else "N/A"

    rows = table.find_all("tr")
    if len(rows) > 1:
        columns = rows[1].find_all("td")
        manufacturer = columns[1].get_text(strip=True) if len(columns) > 1 else "N/A"
        description = columns[2].get_text(strip=True) if len(columns) > 2 else "N/A"
    else:
        manufacturer = description = "N/A"

    return {
        "supplier": found_supplier or "Unknown",
        "product_part_number": product_part_number,
        "supplier_part_number": disti_number,
        "manufacturer": manufacturer,
        "description": description,
    }


if __name__ == "__main__":
    part_number = "NACE100M100V6.3X8TR13F"
    supplier = "Avnet Americas"
    result = extract_findchips(part_number, supplier)
    print(result)
