import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class SupplierInfo:
    supplier_name: Optional[str] = None
    supplier_address: Optional[str] = None
    supplier_email: Optional[str] = None
    supplier_phone: Optional[str] = None


# ------------------------
# Normalização básica
# ------------------------
def _normalize_text(text: str) -> Tuple[str, List[str]]:
    # Normaliza quebras de linha e espaços
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    # remove linhas totalmente vazias
    lines = [ln for ln in lines if ln]
    return text, lines


# ------------------------
# Detecção de "perfil" do fornecedor
# ------------------------
def _detect_supplier_profile(text: str) -> str:
    up = text.upper()

    # Mouser
    if (
        "MOUSER ELECTRONICS" in up
        or "MOUSER.COM" in up
        or "AMERICAS.REMIT@MOUSER.COM" in up
        or "1000 NORTH MAIN STREET" in up and "MANSFIELD" in up
    ):
        return "mouser"

    # Avnet
    if "AVNET" in up:
        return "avnet"

    # XWORK Solutions
    if "XWORK SOLUTIONS" in up or "XWORKSOLUTIONS.COM" in up:
        return "xwork"

    # genérico
    return "generic"


# ------------------------
# Extração genérica de e-mail
# ------------------------
def _extract_email(text: str, preferred_domains: Optional[List[str]] = None) -> Optional[str]:
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if not emails:
        return None

    if preferred_domains:
        for dom in preferred_domains:
            for em in emails:
                if dom.lower() in em.lower():
                    return em

    # fallback: primeiro e-mail
    return emails[0]


# ------------------------
# Extração genérica de telefone
# (somente números com separadores, pra não confundir com PN)
# ------------------------
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s\-\.])?(?:\(?\d{2,4}\)?[\s\-\.])?\d{3,5}[\s\-\.]\d{3,5}"
)


def _extract_phone(lines: List[str]) -> Optional[str]:
    # 1) Tenta primeiro linhas com palavras-chave
    key_words = ("PHONE", "TEL", "TOLL FREE", "PH:")
    for line in lines:
        up = line.upper()
        if any(k in up for k in key_words):
            m = PHONE_PATTERN.search(line)
            if m and not re.search(r"[A-Za-z]", m.group()):
                return m.group().strip()

    # 2) Fallback: varrer tudo
    for line in lines:
        m = PHONE_PATTERN.search(line)
        if m and not re.search(r"[A-Za-z]", m.group()):
            return m.group().strip()

    return None


# ------------------------
# Heurísticas genéricas para NOME e ENDEREÇO
# ------------------------
_SUPPLIER_NAME_KEYWORDS = {
    "ELECTRONICS",
    "ELECTRONIC",
    "INDUSTRIAL",
    "MARKETING",
    "CORP",
    "CORPORATION",
    "LIMITED",
    "LTD",
    "LTDA",
    "S.A.",
    "GMBH",
    "SOLUTIONS",
    "TECHNOLOGIES",
    "TECNOLOGIA",
    "COMPANY",
    "CO.",
    "INC",
}


def _looks_like_supplier_name(line: str) -> bool:
    up = line.upper()

    # Ignorar TECSYS (cliente)
    if "TECSYS" in up:
        return False

    # Não pode ser linha de item (começando com número + data + etc)
    if re.match(r"^\d{1,3}\s+\d{2}/\d{2}/\d{2,4}", line):
        return False

    # Tem alguma palavra "típica" de razão social?
    if any(k in up for k in _SUPPLIER_NAME_KEYWORDS):
        return True

    # Ou é uma linha toda em maiúsculas razoável, sem ser texto genérico
    if up == line and 5 <= len(line) <= 80 and "INVOICE" not in up and "BILL TO" not in up:
        return True

    return False


def _extract_name_generic(lines: List[str]) -> Optional[str]:
    # 1) prioriza linhas com "Company:"
    for line in lines:
        if "COMPANY:" in line.upper():
            # pega o texto após "Company:"
            parts = line.split(":", 1)
            if len(parts) == 2:
                cand = parts[1].strip()
                if cand and "TECSYS" not in cand.upper():
                    return cand

    # 2) usa heurística de "parece razão social"
    for line in lines:
        if _looks_like_supplier_name(line):
            return line.strip()

    return None


_ADDRESS_HINT_WORDS = (
    "STREET",
    "ST.",
    "AVENUE",
    "AVE",
    "ROAD",
    "RD",
    "DRIVE",
    "DR",
    "BOULEVARD",
    "BLVD",
    "LANE",
    "LN",
    "WAY",
    "HIGHWAY",
    "HWY",
    "RUA",
    "AV.",
    "AV ",
    "AVENIDA",
    "ROD.",
    "ESTRADA",
    "ZIP",
    "CEP",
    "TX",
    "SP",
    "USA",
    "BRASIL",
    "BRAZIL",
)


def _line_looks_like_address(line: str) -> bool:
    up = line.upper()

    # tem pelo menos um dígito
    if not re.search(r"\d", line):
        return False

    # precisa ter alguma palavra típica de endereço
    if not any(w in up for w in _ADDRESS_HINT_WORDS):
        return False

    # não pode conter "PN:" (linha de item)
    if "PN:" in up:
        return False

    # não pode ser linha com muitos campos numéricos tipo item
    if re.match(r"^\d{1,3}\s+\d{2}/\d{2}/\d{2,4}", line):
        return False

    return True


def _extract_address_generic(lines: List[str], name_idx: Optional[int]) -> Optional[str]:
    # Se soubermos a linha do nome, começamos a procurar endereço mais abaixo
    start = 0
    if name_idx is not None:
        start = name_idx + 1

    best = []

    # procura até algumas linhas abaixo
    for idx in range(start, min(len(lines), start + 10)):
        line = lines[idx]
        if _line_looks_like_address(line):
            best.append(line)
            # tenta incluir 1–2 linhas logo abaixo se forem parecidas
            for j in range(idx + 1, min(len(lines), idx + 3)):
                if _line_looks_like_address(lines[j]):
                    best.append(lines[j])
            break

    if not best:
        return None

    addr = " ".join(best)
    # corta qualquer coisa depois de " * Número de Referência", se existir
    addr = re.split(r"\*\s*N[úu]mero de Refer[êe]ncia", addr, flags=re.IGNORECASE)[0].strip()
    return addr or None


# ------------------------
# Perfis específicos
# ------------------------
def _extract_mouser(lines: List[str], text: str) -> SupplierInfo:
    up = text.upper()
    name = "Mouser Electronics"

    # tenta pegar da linha "Company: ..."
    for line in lines:
        if "COMPANY:" in line.upper() and "MOUSER" in line.upper():
            parts = line.split(":", 1)
            if len(parts) == 2:
                cand = parts[1].strip()
                if cand:
                    name = cand
            break

    # endereço preferencial: o da sede de Mansfield, TX
    addr = None
    for line in lines:
        up_line = line.upper()
        if "1000 NORTH MAIN STREET" in up_line:
            addr = line.strip()
            # tenta pegar a próxima linha se tiver cidade/estado
            idx = lines.index(line)
            if idx + 1 < len(lines):
                nxt = lines[idx + 1].strip()
                if "MANSFIELD" in nxt.upper() or "TX" in nxt.upper():
                    addr = addr + " " + nxt
            break

    # se não achar por esse caminho, usa heurística genérica perto do nome
    if addr is None:
        name_idx = None
        for i, line in enumerate(lines):
            if "MOUSER" in line.upper():
                name_idx = i
                break
        addr = _extract_address_generic(lines, name_idx)

    email = _extract_email(text, preferred_domains=["mouser.com"])

    phone = _extract_phone(lines)

    return SupplierInfo(
        supplier_name=name,
        supplier_address=addr,
        supplier_email=email,
        supplier_phone=phone,
    )


def _extract_avnet(lines: List[str], text: str) -> SupplierInfo:
    name = None
    for line in lines:
        if "AVNET" in line.upper():
            # remove sufixos tipo (000034/02)
            name = re.sub(r"\s*\(.*?\)\s*$", "", line).strip()
            break

    # se ainda não tiver nome, usa genérico
    if not name:
        name = _extract_name_generic(lines)

    # tenta achar endereço em alguma linha logo abaixo do nome
    name_idx = None
    if name:
        for i, line in enumerate(lines):
            if name in line:
                name_idx = i
                break

    addr = _extract_address_generic(lines, name_idx)
    email = _extract_email(text, preferred_domains=["avnet.com"])
    phone = _extract_phone(lines)

    return SupplierInfo(
        supplier_name=name,
        supplier_address=addr,
        supplier_email=email,
        supplier_phone=phone,
    )


def _extract_xwork(lines: List[str], text: str) -> SupplierInfo:
    name = None
    for line in lines:
        if "XWORK SOLUTIONS" in line.upper():
            name = line.strip()
            break
    if not name:
        name = "XWORK SOLUTIONS CORP"

    # endereço: linha que contenha "MIAMI" ou "FL - 33176"
    addr = None
    for line in lines:
        up = line.upper()
        if "MIAMI" in up or "FL - 33176" in up:
            addr = line.strip()
            break

    email = _extract_email(text, preferred_domains=["xworksolutions.com"])

    # telefone: linha com "PH:" preferencialmente
    phone = None
    for line in lines:
        if "PH:" in line.upper():
            m = PHONE_PATTERN.search(line)
            if m and not re.search(r"[A-Za-z]", m.group()):
                phone = m.group().strip()
                break

    if not phone:
        phone = _extract_phone(lines)

    return SupplierInfo(
        supplier_name=name,
        supplier_address=addr,
        supplier_email=email,
        supplier_phone=phone,
    )


def _extract_generic(lines: List[str], text: str) -> SupplierInfo:
    name = _extract_name_generic(lines)

    name_idx = None
    if name:
        for i, line in enumerate(lines):
            if name in line:
                name_idx = i
                break

    addr = _extract_address_generic(lines, name_idx)
    email = _extract_email(text)
    phone = _extract_phone(lines)

    return SupplierInfo(
        supplier_name=name,
        supplier_address=addr,
        supplier_email=email,
        supplier_phone=phone,
    )


# ------------------------
# Função principal pública
# ------------------------
def extract_supplier(text: str) -> SupplierInfo:
    """
    Extrai informações do fornecedor a partir do texto completo do PDF.

    Estratégia AB:
      1) Detecta 'perfil' do fornecedor (Mouser, Avnet, XWork, genérico)
      2) Usa regras específicas se for um perfil conhecido
      3) Cai na heurística genérica caso contrário
    """
    norm_text, lines = _normalize_text(text)
    profile = _detect_supplier_profile(norm_text)

    if profile == "mouser":
        return _extract_mouser(lines, norm_text)
    if profile == "avnet":
        return _extract_avnet(lines, norm_text)
    if profile == "xwork":
        return _extract_xwork(lines, norm_text)

    # fallback genérico
    return _extract_generic(lines, norm_text)
