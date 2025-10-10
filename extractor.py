from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extrair_findchips(part_number, fornecedor_alvo=None):
    url = f"https://www.findchips.com/search/{part_number}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        page = browser.new_page()
        print(f"[INFO] Acessando {url}...")
        page.goto(url, timeout=60000)
        page.wait_for_selector("table", timeout=20000)
        page.wait_for_timeout(3000)

        # Coleta todos os nomes de fornecedores
        fornecedores = page.eval_on_selector_all(
            "h3",
            "elements => elements.map(el => el.textContent.trim()).filter(t => t.length > 0)"
        )

        # Filtra “Most Popular Part Numbers”
        fornecedores_validos = [f for f in fornecedores if "Most Popular" not in f]

        fornecedor_encontrado = None
        if fornecedor_alvo:
            for f in fornecedores_validos:
                if fornecedor_alvo.lower() in f.lower():
                    fornecedor_encontrado = f
                    break

        # Se não encontrar, pegar o primeiro fornecedor real
        if not fornecedor_encontrado and fornecedores_validos:
            fornecedor_encontrado = fornecedores_validos[0]

        # Extrair o DISTI #
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

    # pegar o part number principal
    tabela = soup.find("table")
    if not tabela:
        return "Tabela não encontrada."

    part_number_produto = tabela.find("a")
    part_number_produto = part_number_produto.get_text(strip=True) if part_number_produto else "N/A"

    linhas = tabela.find_all("tr")
    if len(linhas) > 1:
        colunas = linhas[1].find_all("td")
        fabricante = colunas[1].get_text(strip=True) if len(colunas) > 1 else "N/A"
        descricao = colunas[2].get_text(strip=True) if len(colunas) > 2 else "N/A"
    else:
        fabricante = descricao = "N/A"

    return {
        "fornecedor": fornecedor_encontrado or "Desconhecido",
        "part_number_produto": part_number_produto,
        "part_number_fornecedor": disti_number_js or "N/A",
        "fabricante": fabricante,
        "descricao": descricao
    }


if __name__ == "__main__":
    part_number = "1N4148W-TP"
    fornecedor = "Newark"  # Pode trocar para testar com outro
    resultado = extrair_findchips(part_number, fornecedor)
    print(resultado)
