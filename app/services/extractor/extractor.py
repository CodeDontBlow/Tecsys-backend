from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_findchips(part_number, targed_supplier=None):
    url = f"https://www.findchips.com/search/{part_number}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        page = browser.new_page()
        print(f"[INFO] Acessando {url}...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("table", timeout=20000)
        page.wait_for_timeout(3000)

        # Collect all suppliers' name
        suppliers = page.eval_on_selector_all(
            "h3",
            "elements => elements.map(el => el.textContent.trim()).filter(t => t.length > 0)"
        )

        # Filter “Most Popular Part Numbers”
        valid_suppliers = [f for f in suppliers if "Most Popular" not in f]

        found_supplier = None
        if targed_supplier:
            for f in valid_suppliers:
                if targed_supplier.lower() in f.lower():
                    found_supplier = f
                    break

        # If it doesn't find, it gets the first one
        if not found_supplier and valid_suppliers:
            found_supplier = valid_suppliers[0]

        # Extract the DISTI #
        disti_number_js = page.eval_on_selector_all(
            "div, td, span",
            """elements => {
                for (const el of elements) {
                    if (el.textContent && el.textContent.includes('DISTI #')) {
                        const match = el.textContent.match(/DISTI #\\s*([A-Za-z0-9\\-_.]+)/);
                        if (match) return match[1];
                    }
                }
                return '';
            }"""
        )

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Here, it get the main part number
    table = soup.find("table")
    if not table:
        return "table not found."

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
        "supplier": found_supplier or "Desconhecido",
        "product_part_number": product_part_number,
        "part_number_fornecedor": disti_number_js or "N/A",
        "manufacturer": manufacturer,
        "description": description
    }


if __name__ == "__main__":
    part_number = "1N4148W-TP"
    supplier = "Newark" 
    result = extract_findchips(part_number, supplier)
    print(result)
