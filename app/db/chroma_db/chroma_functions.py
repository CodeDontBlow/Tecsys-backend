import chromadb
import uuid
import pandas as pd
import logging
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def create_collection(name_collection: str):

    path: str = "app/db/chroma_db/chroma.db"
    ollama_url: str = "http://localhost:11434/api/embeddings"
    embedding_model: str = "nomic-embed-text"

    client = chromadb.PersistentClient(path)

    ollama_ef = OllamaEmbeddingFunction(
        url=ollama_url,
        model_name=embedding_model,
    )
    
    try:
        collection = client.get_collection(
            name=name_collection,
            embedding_function=ollama_ef
        )
        logger.info(f"Collection '{name_collection}' already exists.")
        return collection
    except:
        collection = client.create_collection(
            name=name_collection,
            embedding_function=ollama_ef
        )
        logger.info(f"Collection '{name_collection}' created with Ollama embedding function.")
        return collection
    
def populate_collection(path_csv:str, collection):
    
    if collection.count() > 0:
        logger.info(f"Collection already has {collection.count()} items.")
        return

    df = pd.read_csv(path_csv)
    for _, row in df.iterrows():
        code_ncm = row["Codigo"]
        description_ncm = row["Descricao"]

        collection.add(
            ids=[str(uuid.uuid4())],
            documents=[description_ncm],  
            metadatas=[{"codigo_ncm": code_ncm}]
        )
    
    logger.info(f"Collection populated with {len(df)} items!")

def search_in_collection(collection, query: str, n_results: int):
    results = collection.query(
        query_texts=[query], 
        n_results=n_results,
    )
    logger.info(f"Search completed for: '{query}'")
    return results