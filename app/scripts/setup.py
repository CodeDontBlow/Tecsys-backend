import subprocess
import sys
import os
import ollama
import logging
from app.util.tipi.table_tipi import fetch_tipi_data
from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.config import EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ollama():
    try:
        logger.info(f"Checking ollama version {EMBEDDING_MODEL} in system.")
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        version_line = result.stdout.strip()
        logger.info(f"Ollama version found: {version_line}")
    except FileNotFoundError:
        logger.error("Ollama not found. Install: https://ollama.com/download")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error Ollama: {e}")
        sys.exit(1)
    
def pull_ollama_model_embedding():
    try:
        logger.info(f"Start pulling embedding model {EMBEDDING_MODEL}")
        subprocess.run(["ollama", "pull",EMBEDDING_MODEL], check=True)
        logger.info(f"Success downloaded: {EMBEDDING_MODEL}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloaded: {EMBEDDING_MODEL}")
        sys.exit(1)

def pull_ollama_model_description():
    try:
        caminho = os.path.abspath('./app/services/ollama_service/modelfile')
        logger.info(f"Start pulling and create model based on modelfile ") 
        subprocess.run(
            ['ollama', 'create', 'descriptum', '-f', caminho],
        )
        logger.info(f"Success downloaded and created model Descriptum:latest")
        
    except subprocess.CalledProcessError as e:
        logger.info(f"Error in command execution: {e}")
        logger.info("Stderr:", e.stderr)
        return None
    except FileNotFoundError:
        logger.info("Error: 'ollama command not found, check ollama is installed'.")
        return None    
 

def config_system_tools():
    try:
        logger.info("START CONFIG DOWNLOAD")
        logger.info("Ollama verify")
        check_ollama()
        pull_ollama_model_embedding()
        pull_ollama_model_description()
        logger.info("Table TIPI verify")
        fetch_tipi_data()
        logger.info("Chromadb verify")
        chroma_manager.populate_from_csv()
    except Exception as e:
        logger.error(f"Erro during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    config_system_tools()