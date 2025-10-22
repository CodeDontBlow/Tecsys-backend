from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from .config import EMBEDDING_MODEL

def get_embedding_ollama() -> OllamaEmbeddingFunction:
    embedding_model: str = EMBEDDING_MODEL    
    
    return OllamaEmbeddingFunction(
        model_name=embedding_model,
        timeout=60  
    )