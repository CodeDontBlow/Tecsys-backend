import re
from typing import List


def extract_part_numbers(text: str) -> List[str]:

    pn_regex = r"\b([A-Za-z0-9][A-Za-z0-9\-_.]{3,})\b"
    candidates = re.findall(pn_regex, text)

    final = []

    for tok in candidates:
        t = tok.strip()
        upper = t.upper()

        # ---------------------------
        # 1) EXCLUSÕES (devem vir ANTES)
        # ---------------------------

        # telefone
        if re.match(r"^\d{2}-\d{2}-\d{4}-\d{4}$", t):
            continue

        # CEP
        if re.match(r"^\d{5}-\d{3}$", t):
            continue

        # datas / períodos
        if re.match(r"^\d{1,2}[-/]\d{1,4}$", t):
            continue

        # Só letras → não é PN
        if t.isalpha():
            continue

        # Número puro < 10 dígitos → não é PN
        if t.isdigit() and len(t) < 10:
            continue

        # HS CODE / SCHEDULE B
        if t.isdigit() and len(t) == 10 and t.startswith(("84", "85", "86", "87", "90")):
            continue

        # terminações técnicas comuns
        if upper.endswith(("MM", "DEG", "PF", "MHZ")):
            continue

        # códigos técnicos não-PN
        if re.match(r"(RG|[0-9]POS|[0-9]MM|[0-9]PF)", upper):
            continue

        # códigos de lote
        if re.match(r"^E\d{6,}", upper):
            continue

        # domínio
        if "." in t and not any(c.isdigit() for c in t):
            continue

        # faixas numéricas de frequência
        if re.match(r"^\d{3,4}-\d{3,4}$", t):
            continue

        # palavras compostas sem números (ex.: UP-RIGHT)
        if re.match(r"^[A-Za-z\-]+$", t) and not any(c.isdigit() for c in t):
            continue

        # blacklist forte
        blacklist = {
            "EX-WORKS", "WORKS", "INVOICE", "TOTAL",
            "INFORMATION", "DECLARE", "CONTAINED",
            "CORRECT", "ITEM", "DESC", "MFR", "SCHEDULE",
            "LOT", "COO", "PAGE"
        }
        if upper in blacklist:
            continue

        # faixas numéricas de frequência
        if re.match(r"^\d{3,4}-\d{3,4}$", t):
            continue

        # palavras compostas sem números (UP-RIGHT)
        if re.match(r"^[A-Za-z\-]+$", t) and not any(c.isdigit() for c in t):
            continue

        # CEP com ponto
        if re.match(r"^\d{2}\.\d{3}-\d{3}$", t):
            continue

        # packages SMD conhecidos
        package_keywords = {"DO-214AC", "SMA", "DFN", "TO-220", "QFN", "BGA", "SOIC"}
        if upper in package_keywords:
            continue


        # capacitâncias e valores elétricos
        if upper.endswith(("UF", "NF", "PF", "MF")):
            continue

        # tensões / certificações / classes
        if upper.endswith(("VAC", "VDC", "AC", "X1", "X2")):
            continue

        # frequências
        if upper.endswith(("HZ", "KHZ", "MHZ", "GHZ")):
            continue

        # tamanhos tipo 12.5X25 ou 6X12
        if re.match(r"^\d+(\.\d+)?x\d+(\.\d+)?$", t, re.IGNORECASE):
            continue

        # pacotes SMD / encapsulamentos
        packages = {
            "DFN-12", "SMA", "DO-214AC", "SOT-23", "QFN", "BGA",
            "SOIC", "TO-220", "TO-92", "LGA", "LCC"
        }
        if upper in packages:
            continue


        # -------------------------------------
        # ACEITAR PNs alfanuméricos SEM hífen:
        # ex: LTC3625EDE#PBF, AHEF1000, 132119, 132119RP
        # -------------------------------------
        if len(t) >= 6 and any(c.isalpha() for c in t) and any(c.isdigit() for c in t):
            final.append(t)
            continue


        # ---------------------------
        # 2) ACEITAÇÕES (somente aqui)
        # ---------------------------

        # PN numérico longo (10+ dígitos)
        if t.isdigit() and len(t) >= 10:
            final.append(t)
            continue

        # híbridos longos com "-"
        if "-" in t and len(t) >= 8:
            final.append(t)
            continue

        # alfanuméricos longos
        if len(t) >= 12 and any(c.isalpha() for c in t):
            final.append(t)
            continue

    # unique
    uniq = []
    for p in final:
        if p not in uniq:
            uniq.append(p)

    return uniq
