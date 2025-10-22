import requests
import pandas as pd
import logging
import io
from pathlib import Path
from app.db.chroma_db.config import CSV_PATH
import re
from collections import Counter
from app.log.logger import logger

#------------- fetch tipi data -------------
def fetch_tipi_data(
    url: str = "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/legislacao/documentos-e-arquivos/tipi.xlsx",
    output_csv: str = "app/util/tipi/tipi_chapter_85.csv",
    filter_number: str = "85",
    sheet_name: str | int = 0,
) -> None:
    
    output_path = Path(output_csv)
    if output_path.exists():
        logger.info(f"[TIPI] File already exists: {output_csv}")
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"[TIPI] Fetching TIPI data from: {url}")
        
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        logger.info("[TIPI] Successfully downloaded TIPI XLSX")

        df = pd.read_excel(io.BytesIO(resp.content), sheet_name=sheet_name, skiprows=7, engine="openpyxl")
        df.columns = [str(c).strip().lower() for c in df.columns]

        col_ncm = next((c for c in df.columns if "ncm" in c), None)
        if not col_ncm:
            raise ValueError(f"[TIPI] Not found column: {df.columns}")
        
        df_filtered = df[df[col_ncm].astype(str).str.startswith(filter_number)]

        df_filtered.to_csv(output_csv, index=False, encoding="utf-8")
        logger.info(f"[TIPI] Generated {output_csv} with {len(df_filtered)} records filtered by chapter {filter_number}")

    except requests.exceptions.RequestException as e:
        logger.error(f"[TIPI] Error requesting TIPI XLSX: {e}")
        raise
    except Exception as e:
        logger.error(f"[TIPI] Unexpected error: {e}")
        raise


#------------- only verify terms most repeated -------------
def formated(text:str):
    stopwords = {"de", "a", "o", "os", "as", "em", "até", "com", "para", "e", "ou", "por", "na", "no"}

    text = re.sub(r"[^\w\s]", " ", text.lower()) 
    text_list = text.split() 
    return [t for t in text_list if t not in stopwords] 

def most_terms_repeated():
    csv:str = CSV_PATH
    
    df = pd.read_csv(csv)
    descriptions = df["descrição"].dropna().tolist()

    counter = Counter()
    for d in descriptions:
        formated_text = formated(d)
        counter.update(formated_text) 

    most_common_terms = counter.most_common(1000)
    
    print("Terms most common:")
    for term, freq in most_common_terms:
        print(f"{term}: {freq}")

def formated_query(query: str) -> str:
    key_terms = {
        "geral": ["outros", "aparelhos", "elétricos", "superior", "inferior",
                  "montados", "incluindo", "exceto", "partes", "montagem"],
        "eletronicos": ["diodo", "led", "circuito", "transistor", "resistencia", "condensador",
                         "semicondutor", "dispositivo", "integrado", "memoria",
                        "eprom", "eeprom", "flash", "smd", "chipset", "driver", "controlador",
                        "sensor", "microfone", "altofalante", "amplificador", "receptor", "transmissor"],
        "eletricos": ["motor", "gerador", "transformador", "bobina", "tubo", "pilha", "bateria",
                      "fusivel", "disjuntor", "condutor", "painel", "chave",
                      "interruptor", "lampada"],
        "comunicacao": ["televisao", "radio", "telefone", "antena", "modem", "roteador", "hub",
                        "switch", "sinal", "repetidor", "satelite", "transmissao"],
        "materiais": ["cobre", "ferro", "aluminio", "plastico", "vidro", "ceramica", "resina",
                      "cadmio", "chumbo", "mercurio", "policlorobifenilas", "tantalo"],
        "outras_funcoes": ["aquecimento", "iluminacao", "ar", "refrigeracao", "energia", "controle",
                           "processamento", "armazenamento", "visualizacao", "captura", "deteccao",
                           "regulacao", "protecao", "isolante", "conexao", "suporte", "medicao",
                           "conversores"]
    }

    words = query.lower().replace(",", " ").replace("(", " ").replace(")", " ").split()
    detected_terms = []

    if "Cerâmico" in query:
        detected_terms.append("cerâmica")
    
    if "SMD" in query:
        detected_terms.append("montagem")


    if "Indutor" in query:
        query = query.replace("Indutor", "").strip()  
        detected_terms.append("bobinas")
        detected_terms.append("reatância")
        detected_terms.append("autoindução")

    for cat_terms in key_terms.values():
        for term in cat_terms:
            if term in words:
                detected_terms.append(term)

    return " ".join(detected_terms) + " " + query