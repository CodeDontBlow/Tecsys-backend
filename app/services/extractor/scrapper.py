import time
import os
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout #type: ignore

# Cabeçalhos para simular uma requisição de navegador e evitar bloqueios (sem isso, nem todas as informações do site são extraídas).
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36",
"Accept-Language": "en-US,en;q=0.9"}
DEFAULT_SLEEP_BETWEEN_REQUESTS = 1.0
REQUESTS_TIMEOUT = 20

OUTPUT_DIR = os.path.join("app", "scripts", "web-scraping", "scraper_results", f"scrape_{time.strftime('%Y-%m-%d_%H-%M-%S')}")

def ensure_dir(outdir):
    os.makedirs(outdir, exist_ok=True)
    return outdir

def save_text(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def get_raw_html_from_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUESTS_TIMEOUT)
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter o HTML da URL {url}: {e}")
        return None

def get_rendered_html_from_url(url):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(user_agent=HEADERS["User-Agent"], locale="en-US")
            page = context.new_page()

            page.goto(url, timeout=60_000)
            page.wait_for_load_state("networkidle", timeout=30_000)

            time.sleep(1.5)

            rendered = page.content()
            page.close()
            context.close()
            browser.close()

            return rendered
        except PWTimeout:
            print(f"Erro: O carregamento da página {url} demorou demais.")
            return None

def save_combined_html(raw_html, rendered_html, outdir, pn):
    combined_html_path = os.path.join(outdir, f"{pn}.html")
    
    combined_html_content = f"""
    <html>
    <body>
        <pre>{raw_html}</pre>
        <pre>{rendered_html}</pre>
    </body>
    </html>
    """

    save_text(combined_html_content, combined_html_path)
    print(f"Arquivo HTML do PN {pn} salvo em {combined_html_path}.")

def process_pn(pn, outdir, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS):
    url = f"https://www.findchips.com/search/{pn}"
    print(f"\nIniciando o processamento do PN: {pn}...")

    raw_html = get_raw_html_from_url(url)
    if not raw_html:
        print(f"Erro ao obter o HTML para o PN {pn}. Pulando...")
        return

    time.sleep(sleep_between)

    rendered_html = get_rendered_html_from_url(url)
    if not rendered_html:
        print(f"Erro ao obter o HTML renderizado para o PN {pn}. Pulando...")
        return

    time.sleep(sleep_between)

    save_combined_html(raw_html, rendered_html, outdir, pn)

def main():
    pns = ["NACE100M100V6.3X8TR13F", "1N4148W-TP"]
    
    if not pns:
        print("Nenhum PN encontrado na lista.")
        return

    outdir = ensure_dir(OUTPUT_DIR)
    print(f"Iniciando o processamento de {len(pns)} PNs. Os arquivos serão salvos em: {outdir}")

    for pn in pns:
        process_pn(pn, outdir, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS)

if __name__ == "__main__":
    main()