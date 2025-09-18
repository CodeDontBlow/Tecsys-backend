import logging
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_embedding_ollama() -> OllamaEmbeddingFunction:
    ollama_url: str = "http://localhost:11434/api/embeddings"
    embedding_model: str = "bge-m3:latest"

    logger.info(f"Inicializando OllamaEmbeddingFunction | URL={ollama_url}, Modelo={embedding_model}")
    
    return OllamaEmbeddingFunction(url=ollama_url, model_name=embedding_model)




    
