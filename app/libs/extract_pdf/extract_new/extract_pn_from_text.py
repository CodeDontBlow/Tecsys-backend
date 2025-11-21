import re
from typing import List


def extract_part_numbers(text: str) -> List[str]:
    """
    Extrai possíveis Part Numbers (PNs) de um texto cru.

    Estratégia (v3.0):
    - Regex bem genérico para pegar tokens "candidatos" (letras/dígitos + [-_.]).
    - Vários filtros de EXCLUSÃO (telefone, CEP, datas, HS Code, medidas, pacotes SMD, etc.).
    - Regras específicas para alguns fornecedores (Mouser, Tecsys).
    - Só depois aplicamos regras de ACEITAÇÃO para decidir se um token é PN.
    - No final, removemos duplicados mantendo a ordem original.
    """

    # Normalizamos uma cópia em maiúsculas para detecção de fornecedor
    upper_text = text.upper()

    is_mouser = (
        "MOUSER ELECTRONICS" in upper_text
        or "WWW.MOUSER.COM" in upper_text
        or "MOUSER BRASIL" in upper_text
    )
    is_tecsys = (
        "TECSYS DO BRASIL" in upper_text
        or "XWORKSOLUTIONS.COM" in upper_text
    )

    # Regex "genérica" de candidatos a PN:
    #  - começa com letra/dígito
    #  - depois 3+ caracteres de [letra, dígito, -, _, .]
    pn_regex = r"\b([A-Za-z0-9][A-Za-z0-9\-_.]{3,})\b"
    candidates = re.findall(pn_regex, text)

    # Listas de apoio
    generic_blacklist = {
        # termos de invoice / administrativos
        "EX-WORKS", "WORKS", "INVOICE", "TOTAL", "SUBTOTAL",
        "INFORMATION", "DECLARE", "CONTAINED", "CORRECT",
        "ITEM", "DESC", "MFR", "SCHEDULE", "LOT", "COO", "PAGE",
        "CUSTOMER", "NUMBER", "PAYMENT", "TERMS", "SHIP", "INCOTERM",
        "INVOICE#", "INVOICENO",

        # pesos / medidas gerais
        "N.WT", "G.WT", "NWT", "GWT",

        # termos administrativos mais chatos
        "ANTI-CORRUPTION", "END-USER", "ENDUSER",
        "ENVIE-NOS", "ENVIENOS", "END-USE",

        # descrições genéricas
        "RETURN", "LOSS", "GAIN", "MOUNT", "SOURCE",
        "HARDWARE", "EMBEDDED", "COMPUTER", "LINUX",
        "SINGLE", "BOARD",

        # coisas de CPU / SoC
        "ARM926J",
    }

    # pacotes/encapsulamentos comuns (não queremos como PN)
    package_tokens = {
        "DFN-12", "DFN12",
        "SMA", "DO-214AC", "SOT-23", "SOT-223", "SOT-523", "SOT-723",
        "QFN", "BGA", "SOIC",
        "TO-220", "TO-252-3", "TO-252", "TO252", "TO-92", "LGA", "LCC",
    }

    # resultado final
    final: List[str] = []

    for tok in candidates:
        t = tok.strip()
        if not t:
            continue

        upper = t.upper()

        # ---------------------------
        # 1) EXCLUSÕES UNIVERSAIS
        # ---------------------------

        # a) telefones: 0000-0000, 12-3456-7890, etc.
        if re.match(r"^\d{4}-\d{4}$", t):
            continue
        if re.match(r"^\d{2,3}-\d{3,4}-\d{3,4}$", t):
            continue

        # b) CEP: 12345-678 ou 12.345-678
        if re.match(r"^\d{5}-\d{3}$", t):
            continue
        if re.match(r"^\d{2}\.\d{3}-\d{3}$", t):
            continue

        # c) datas / períodos: 3-2025, 03-2025, 3/5/2025 etc.
        if re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$", t):
            continue
        if re.match(r"^\d{1,2}[-/]\d{1,4}$", t):
            continue

        # d) só letras → não é PN
        if t.isalpha():
            continue

        # e) faixa numérica tipo 1700-2700 (frequência)
        if re.match(r"^\d{3,4}-\d{3,4}$", t):
            continue

        # f) domínio/host sem dígitos (ex: "xworksolutions.com")
        if "." in t and not any(c.isdigit() for c in t):
            continue

        # g) palavras compostas por letras e hífen, mas sem dígitos (UP-RIGHT, ITEM-CLIENTE)
        if re.match(r"^[A-Za-z\-]+$", t) and not any(c.isdigit() for c in t):
            continue

        # h) blacklist forte (palavras que NUNCA queremos como PN)
        if upper in generic_blacklist:
            continue

        # i) tokens de pacote/encapsulamento (SOT-23, DFN-12, etc.)
        if upper in package_tokens:
            continue

        # j) terminações técnicas de unidade (medida, capacitância, etc.)
        if upper.endswith(("MM", "CM", "IN")):
            continue
        if upper.endswith(("UF", "NF", "PF", "MF")):
            continue
        if upper.endswith(("VAC", "VDC", "AC", "X1", "X2")):
            continue
        if upper.endswith(("HZ", "KHZ", "MHZ", "GHZ")):
            continue

        # k) tamanhos tipo 12.5X25 ou 6X12
        if re.match(r"^\d+(\.\d+)?x\d+(\.\d+)?$", t, re.IGNORECASE):
            continue

        # ---------------------------
        # 2) REGRAS ESPECÍFICAS POR FORNECEDOR
        # ---------------------------

        if is_mouser:
            # Códigos internos Mouser tipo 61-1520598 (prefixo numérico + hífen + dígitos)
            if re.match(r"^\d{2,4}-\d{5,}$", t):
                # se NÃO estiver marcado explicitamente como PN:, ignoramos
                if not re.search(rf"PN[:\s]+{re.escape(t)}\b", text, flags=re.IGNORECASE):
                    continue

        if is_tecsys:
            # Códigos internos da Tecsys (ex: 00020020069), numéricos longos
            # Se forem só números 9–12 dígitos e NÃO estiverem em "PN: 00020020069", ignoramos
            if t.isdigit() and 9 <= len(t) <= 12:
                if not re.search(rf"PN[:\s]+{re.escape(t)}\b", text, flags=re.IGNORECASE):
                    continue

        # ---------------------------
        # 3) REGRAS ESPECIAIS PARA NÚMEROS PUROS
        # ---------------------------

        if t.isdigit():
            # HS CODE / SCHEDULE B: 10 dígitos (3926909989, 8536694030, etc.)
            if len(t) == 10:
                continue

            # Só aceitaremos números longos como PN se aparecerem explicitamente após "PN:"
            if re.search(rf"PN[:\s]+{re.escape(t)}\b", text, flags=re.IGNORECASE):
                if t not in final:
                    final.append(t)
            # Se não estiver próximo de "PN:", descartamos
            continue

        # ---------------------------
        # 4) ACEITAÇÕES GERAIS (ALFA + DÍGITO)
        # ---------------------------

        has_alpha = any(c.isalpha() for c in t)
        has_digit = any(c.isdigit() for c in t)

        # a) PNs alfanuméricos "clássicos" (sem depender de hífen)
        #    Ex: LTC3625EDE, AHEF1000, CL10C330JB8NNNC, GRM1885C1H180JA01D
        if len(t) >= 6 and has_alpha and has_digit:
            if t not in final:
                final.append(t)
            continue

        # b) híbridos com hífen e comprimento razoável
        #    Ex: STPS5H100B-TR, ESD7C3.3DT5G, ECS-3225Q-33-260-BS-TR
        if "-" in t and has_digit and len(t) >= 8:
            if t not in final:
                final.append(t)
            continue

        # c) fallback: tokens longos com letras (casos exóticos)
        if len(t) >= 12 and has_alpha:
            if t not in final:
                final.append(t)
            continue

    return final
