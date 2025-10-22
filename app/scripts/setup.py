import subprocess
import sys

from app.util.tipi import table_tipi
from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.config import EMBEDDING_MODEL
from app.log.logger import logger

def check_ollama():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        version_line = result.stdout.strip()
        logger.info(f"[OLLAMA] Ollama version found: {version_line}")

        result_models = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        
        available_models = [
            m.strip().split()[0] 
            for m in result_models.stdout.splitlines() if m.strip()
        ]

        if EMBEDDING_MODEL in available_models:
            logger.info(f"[OLLAMA] Embedding model '{EMBEDDING_MODEL}' is available.")
            return True
        else:
            logger.warning(f"[OLLAMA] Embedding model '{EMBEDDING_MODEL}' not found. ❌")
            return False

    except FileNotFoundError:
        logger.error("[OLLAMA] Ollama not found. Install it: https://ollama.com/download")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"[OLLAMA] Error checking Ollama: {e}")
        raise


def pull_ollama_model_embedding():
    try:
        logger.info(f"[OLLAMA] Start pulling embedding model {EMBEDDING_MODEL}")
        process = subprocess.Popen(
            ["ollama", "pull", EMBEDDING_MODEL],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        for line in process.stdout:
            logger.info(f"[OLLAMA] Ollama pull: {line.strip()}")
            
        process.wait()
        
        if process.returncode == 0:
            logger.info(f"[OLLAMA] Successfully downloaded: {EMBEDDING_MODEL}")
        else:
            logger.error(f"[OLLAMA] Failed to download: {EMBEDDING_MODEL}")
            raise subprocess.CalledProcessError(process.returncode, ["ollama", "pull", EMBEDDING_MODEL])
            
    except subprocess.CalledProcessError as e:
        logger.error(f"[OLLAMA] Error downloading {EMBEDDING_MODEL}: {e}")
        raise
    except Exception as e:
        logger.error(f"[OLLAMA] Unexpected error during model download: {e}")
        raise


def config_system_tools():
    try:
        model_exists = check_ollama()
        
        if not model_exists:
            pull_ollama_model_embedding()
        else:
            logger.info(f"[OLLAMA] Skipping model pull, '{EMBEDDING_MODEL}' already available.") 

        table_tipi.fetch_tipi_data()
        logger.info("[TIPI] File already exists or fetched successfully.")

        chroma_manager.populate_from_csv()
        logger.info("[CHROMADB] Collection populated successfully.")
        
    except Exception as e:
        logger.error(f"[SYSTEM] Error during setup: {e}")
        logger.exception("[SYSTEM] Detailed error:")  
        raise

if __name__ == "__main__":
    try:
        config_system_tools()
    except Exception as e:
        sys.exit(1)