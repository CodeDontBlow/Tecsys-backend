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
    
    #Main Table
    table = soup.find("table")
    if not table:
        logger.warning("[EXTRACTOR] No table found in HTML.")
        return json.dumps({
            "supplier": target_supplier or "Unknown",
            "product_part_number": "N/A",
            "part_number_supplier": disti_number or "N/A",
            "manufacturer": "N/A",
            "description": "N/A"
        }, indent=4, ensure_ascii=False)

    product_part_number = table.find("a")
    product_part_number = product_part_number.get_text(strip=True) if product_part_number else "N/A"


    rows = table.find_all("tr")
    descriptions = []
    manufacturer = "N/A"


    if len(rows) > 1:
        for row in rows[1:]:  # skip header row
            cols = row.find_all("td")
            if len(cols) > 2:
                text = cols[2].get_text(" ", strip=True)
                if text and len(text) > 5:
                    descriptions.append(text)
            # capture manufacturer from the first valid row
            if manufacturer == "N/A" and len(cols) > 1:
                manufacturer = cols[1].get_text(strip=True)

        description = clean_description(" ".join(descriptions))
    else:
        manufacturer = description = "N/A"

    #FALLBACK (description very short)
    if not description or len(description) < 20:
        extra_desc = soup.find_all(
            ["div", "span", "p"],
            string=re.compile(r"(Cap|Res|Diode|Transistor|MOSFET|LDO|Crystal|Oscillator)", re.IGNORECASE)
        )
        extra_texts = [e.get_text(" ", strip=True) for e in extra_desc]
        if extra_texts:
            description = clean_description(" ".join(extra_texts))

    #BUILD FINAL DATA
    data = {
        "supplier": found_supplier or target_supplier,
        "product_part_number": product_part_number,
        "part_number_supplier": disti_number or "N/A",
        "manufacturer": manufacturer,
        "description": description
    }

    logger.info(f"[WEBSCRAPING-EXTRACT] Successfully extracted from {data['product_part_number']}.")
    return json.dumps(data, indent=4, ensure_ascii=False)