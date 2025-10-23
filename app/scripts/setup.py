import subprocess
import time
import sys
import os

from app.util.tipi import table_tipi
from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.config import EMBEDDING_MODEL, DESCRIPTUM_MODEL, CAMINHO_MODELFILE 
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

        if EMBEDDING_MODEL in available_models and DESCRIPTUM_MODEL in available_models:
            logger.info(f"[OLLAMA] Embedding model '{EMBEDDING_MODEL}' and '{DESCRIPTUM_MODEL}' is available.")
            return True
        else:
            if EMBEDDING_MODEL not in available_models:
                logger.warning(f"[OLLAMA] Embedding model '{EMBEDDING_MODEL}' not found. ")
            if DESCRIPTUM_MODEL not in available_models:
                logger.warning(f"[OLLAMA] Descritpum model '{DESCRIPTUM_MODEL}' not found.")
            return False

    except FileNotFoundError:
        logger.error("[OLLAMA] Ollama not found. Install it: https://ollama.com/download")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"[OLLAMA] Error checking Ollama: {e}")
        raise

def loggings_downloading_periodically(process):
    last_log_time = time.time()
    log_interval = 30  
    
    while True:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            time.sleep(0.1)
            continue
            
        current_time = time.time()
        if current_time - last_log_time >= log_interval:
            logger.info(f"[OLLAMA] Still downloading... {line.strip()}")
            last_log_time = current_time


def pull_ollama_model_embedding():
    try:
        logger.info(f"[OLLAMA] Start pulling embedding model {EMBEDDING_MODEL}")
        process = subprocess.Popen(
            ["ollama", "pull", EMBEDDING_MODEL],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8', 
            bufsize=1,
            errors='replace'
        )
        
        logger.info(f"[OLLAMA] Downloading model: '{EMBEDDING_MODEL}'... ")
            
        loggings_downloading_periodically(process)
    
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


def pull_ollama_model_description():
    try:
        caminho = os.path.abspath(CAMINHO_MODELFILE)
        logger.info(f"[OLLAMA] Start pulling and create model '{DESCRIPTUM_MODEL}' based on modelfile ") 
        process = subprocess.Popen(
            ['ollama', 'create', 'descriptum', '-f', caminho],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8', 
            bufsize=1,
            errors='replace'
        )

        logger.info(f"[OLLAMA] Downloading model: 'qwen3:1.7b'...")

        loggings_downloading_periodically(process)

        process.wait()
        
        if process.returncode == 0:
            logger.info(f"[OLLAMA] Success downloaded and created model '{DESCRIPTUM_MODEL}'")

        
    except subprocess.CalledProcessError as e:
        logger.info(f"[OLLAMA] Error in command execution: {e}")
        logger.info("[OLLAMA] Stderr:", e.stderr)
        return None
    except FileNotFoundError:
        logger.info("[OLLAMA] Error: 'ollama command not found, check ollama is installed'.")
        return None    
 

def config_system_tools():
    try:
        model_exists = check_ollama()
        
        if not model_exists:
            pull_ollama_model_embedding()
            pull_ollama_model_description()
        else:
            logger.info(f"[OLLAMA] Skipping model pull, '{EMBEDDING_MODEL}' and '{DESCRIPTUM_MODEL}' already available.") 

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