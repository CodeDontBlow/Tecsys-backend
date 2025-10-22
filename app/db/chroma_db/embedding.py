import logging
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from .config import EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_embedding_ollama() -> OllamaEmbeddingFunction:
    embedding_model: str = EMBEDDING_MODEL
    logger.info(f"Inicializing OllamaEmbeddingFunction | Model={embedding_model}")
    
    return OllamaEmbeddingFunction(
        model_name=embedding_model,
        timeout=60  
    )