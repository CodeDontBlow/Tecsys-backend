import requests
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def fetch_ncm_data(
    url: str = "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json",
    output_csv: str = "app/data/ncm_chapter_85.csv",
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