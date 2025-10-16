import subprocess
import sys

from app.util.tipi import table_tipi
from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.config import EMBEDDING_MODEL
from app.util.logger_info import setup_logger

logger = setup_logger()

def check_ollama():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        version_line = result.stdout.strip()
        logger.info(f"Ollama version found: {version_line}")

        result_models = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        
        available_models = [
            m.strip().split()[0] 
            for m in result_models.stdout.splitlines() if m.strip()
        ]

        if EMBEDDING_MODEL in available_models:
            logger.info(f"Embedding model '{EMBEDDING_MODEL}' is available.")
            return True
        else:
            logger.warning(f"Embedding model '{EMBEDDING_MODEL}' not found. ❌")
            return False

    except FileNotFoundError:
        logger.error("Ollama not found. Install it: https://ollama.com/download")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking Ollama: {e}")
        raise

def pull_ollama_model_embedding():
    try:
        logger.info(f"Start pulling embedding model {EMBEDDING_MODEL}")
        process = subprocess.Popen(
            ["ollama", "pull", EMBEDDING_MODEL],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        for line in process.stdout:
            logger.info(f"Ollama pull: {line.strip()}")
            
        process.wait()
        
        if process.returncode == 0:
            logger.info(f"Successfully downloaded: {EMBEDDING_MODEL}")
        else:
            logger.error(f"Failed to download: {EMBEDDING_MODEL}")
            raise subprocess.CalledProcessError(process.returncode, ["ollama", "pull", EMBEDDING_MODEL])
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading {EMBEDDING_MODEL}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during model download: {e}")
        raise

def config_system_tools():
    try:
        model_exists = check_ollama()
        
        if not model_exists:
            pull_ollama_model_embedding()
        else:
            logger.info(f"Skipping model pull, '{EMBEDDING_MODEL}' already available.") 
        table_tipi.fetch_tipi_data()

        chroma_manager.populate_from_csv()
        
    except Exception as e:
        logger.error(f"Error during setup: {e}")
        logger.exception("Detailed error:")  
        raise

if __name__ == "__main__":
    try:
        logger.info("\n" + "="*50 + " NEW SESSION " + "="*50 + "\n")
        logger.info("=== Starting system configuration ===")
        config_system_tools()
        logger.info("=== System configuration completed successfully ===")
    except Exception as e:
        logger.error(f"=== System configuration failed: {e} ===")
        sys.exit(1)