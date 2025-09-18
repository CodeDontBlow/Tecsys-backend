import requests
import pandas as pd
import logging
from pathlib import Path
from app.db.chroma_db.config import CSV_PATH
import pandas as pd
import re
from collections import Counter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def fetch_ncm_data(
    url: str = "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json",
    output_csv: str = "app/db/chroma_db/ncm_chapter_85.csv",
    filter_number: str = "85",
) -> None:
    
    output_path = Path(output_csv)  
    if output_path.exists():
        logger.info(f"File already exists.")
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # fetch data
        logger.info(f"Fetching data from API: {url}")
        resp = requests.get(url, timeout=30) 
        resp.raise_for_status()
        data = resp.json()
        logger.info("Successfully downloaded data from API")
        
        # filter data by code ncm
        df = pd.DataFrame(data["Nomenclaturas"])
        df_filtered = df[df["Codigo"].astype(str).str.startswith(filter_number)]
        
        # save to CSV
        df_filtered.to_csv(output_csv, index=False)
        logger.info(f"Generated {output_csv} with {len(df_filtered)} records filtered by chapter {filter_number}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting API: {e}")  
        raise
    except KeyError as e:
        logger.error(f"Unexpected data structure from API: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def formated(text:str):
    stopwords = {"de", "a", "o", "os", "as", "em", "até", "com", "para", "e", "ou", "por", "na", "no"}

    text = re.sub(r"[^\w\s]", " ", text.lower()) #transistores exceto os fototransistores
    text_list = text.split() #["transistores" "exceto" "os" "fototransistores"]
    return [t for t in text_list if t not in stopwords] #["Transistores" "exceto" "fototransistores"]

def most_terms_repeated():
    csv:str = CSV_PATH
    
    df = pd.read_csv(csv)
    descriptions = df["Descricao"].dropna().tolist()

    counter = Counter()
    for d in descriptions:
        formated_text = formated(d)
        counter.update(formated_text) 

    most_common_terms = counter.most_common(1000)
    
    print("Terms most common:")
    for term, freq in most_common_terms:
        print(f"{term}: {freq}")