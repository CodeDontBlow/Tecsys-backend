import json
import re
from bs4 import BeautifulSoup

from app.log.logger import logger

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

    suppliers = [h2.get_text(strip=True) for h2 in soup.find_all("h2") if h2.get_text(strip=True)]

    valid_suppliers = [s for s in suppliers if "Most Popular" not in s]

    found_supplier = None
    if target_supplier:
        for s in valid_suppliers:
            if target_supplier.lower() in s.lower():
                found_supplier = s
                break

    if not found_supplier and valid_suppliers:
        found_supplier = valid_suppliers[0]

    disti_number = ''
    for el in soup.find_all(["div", "td", "span"]):
        text = el.get_text()
        if "DISTI #" in text:
            match = re.search(r"DISTI #\s*([A-Za-z0-9\-_.:]+)", text)
            if match:
                disti_number = match.group(1)
                break
    table = soup.find("table")
    if not table:
        return "table not found."

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
        "supplier": found_supplier or target_supplier,
        "product_part_number": product_part_number,
        "part_number_supplier": disti_number or "N/A",
        "manufacturer": manufacturer,
        "description": description
    }

    logger.info(f"[WEBSCRAPING-EXTRACT] Successfully extracted from {data['product_part_number']}.")

    return json.dumps(data,indent=4, ensure_ascii=False)