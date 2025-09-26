from app.db.chroma_db.config import CHROMA_DB_PATH, COLLECTION_NAME, CSV_PATH
from app.db.chroma_db.embedding import get_embedding_ollama, generate_optimized_query
from app.util.text_processing import formated_query
from app.db.chroma_db.model import NCMResult, Response
import chromadb
import pandas as pd
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding = get_embedding_ollama()
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        try:
            collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding
            )
            logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
            return collection
        except:
            collection = self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding
            )
            logger.info(f"Collection '{COLLECTION_NAME}' created.")
            return collection
    
    def populate_from_csv(self):
        if self.collection.count() > 0:
            logger.info(f"Collection already has {self.collection.count()} items.")
            return
        
        df = pd.read_csv(CSV_PATH)
        ids = []
        documents = []
        metadatas = []

        for _, row in df.iterrows():
            code_ncm = row["Codigo"]
            description = row["Descricao"]

            ids.append(str(uuid.uuid4()))
            documents.append(description)
            metadatas.append({
                "codigo_ncm": code_ncm,
                "descricao_original": description,
            })
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Collection populated with {len(df)} items!")


    def search_ncm(self, query: str) -> Response:
        try:
            query_optimized = formated_query(query)
            results = self.collection.query(
                query_texts=[query_optimized],
                n_results=10,
            )

            ncm_results = []
            for i in range(len(results['metadatas'][0])):
                codigo_ncm = results['metadatas'][0][i]['codigo_ncm']
                description = results['documents'][0][i]
                distance = results['distances'][0][i]

                # Se for subposição (8532.24), mantém mas distancia 0
                if len(codigo_ncm) == 7:
                    distance = 0.0

                ncm_results.append(NCMResult(
                    ncm_code=codigo_ncm,
                    description=description,
                    distance=distance
                ))

            return Response(query=query, results=ncm_results)

        except Exception as e:
            logger.error(f"Error to search: {e}")
            return Response(query=query, results=[])
chroma_manager = ChromaDBManager()
        