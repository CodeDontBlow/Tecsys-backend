import json
import logging
import requests
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from .config import EMBEDDING_MODEL,GENERATE_MODEL, OLLAMA_URL_EMBEDDING, OLLAMA_URL_GENERATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_embedding_ollama() -> OllamaEmbeddingFunction:
    ollama_url: str = OLLAMA_URL_EMBEDDING
    embedding_model: str = EMBEDDING_MODEL

    logger.info(f"Inicializando OllamaEmbeddingFunction | URL={ollama_url}, Modelo={embedding_model}")
    
    return OllamaEmbeddingFunction(url=ollama_url, model_name=embedding_model)

def generate_optimized_query(original_query: str) -> str:
    ollama_url: str = OLLAMA_URL_GENERATE
    generation_model: str = GENERATE_MODEL
    
    prompt = f"""
    Sua tarefa é traduzir e normalizar a descrição de um componente eletrônico para português do Brasil.

    REGRAS:
    - Mantenha apenas:
        1. Tipo do componente (ex.: "Diodo", "LED") se relevante
        2. Corrente, se presente (ex.: "2A")
        3. Material específico (ex.: "Eletrolítico de Alumínio")
        4. Embalagem ou montagem (ex.: SMD, PTH). 
        ➜ Se existir, coloque SEMPRE no início da frase.
    - Remova todas as outras informações irrelevantes (palavras incompletas, tensão, tolerância, dimensões, horas de vida, cores, códigos, etc.)
    - A saída deve ser **uma frase curta e concisa**, sem explicações.
    - Não invente palavras ou atributos.

    Agora, processe esta descrição: {original_query}
    """
    
    try:
        response = requests.post(
            ollama_url,
            json={
                "model": generation_model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        generated_text = response.json().get("response", "").strip()
        logger.info(f"Query otimizada gerada: {generated_text}")
        return generated_text if generated_text else original_query
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para o Ollama: {e}")
        return original_query
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao processar a resposta JSON do Ollama: {e}")
        return original_query