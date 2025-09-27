from app.db.chroma_db.config import CHROMA_DB_PATH, COLLECTION_NAME, CSV_PATH
from app.db.chroma_db.embedding import get_embedding_ollama
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
            return self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding
            )
        except:
            return self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding
            )

    def normalize_code(self, code: str) -> str:
        return code.replace(".", "").strip()

    def classify_ncm(self, code: str):
        if len(code) == 2:
            return "capitulo", ""
        elif len(code) == 4:
            return "posicao", code[:2]
        elif len(code) == 6:
            return "subposicao", code[:4]
        elif len(code) == 8:
            return "item", code[:6]
        return "desconhecido", ""
    
    def format_ncm(self, code: str) -> str:
        code = code.strip()
        if len(code) == 2:
            return code
        elif len(code) == 4:
            return f"{code[:2]}{code[2:]}"
        elif len(code) == 6:
            return f"{code[:2]}{code[2:4]}.{code[4:]}"
        elif len(code) == 8:
            return f"{code[:2]}{code[2:4]}.{code[4:6]}.{code[6:]}"
        return code

    def populate_from_csv(self):
        if self.collection.count() > 0:
            logger.info(f"Collection já tem {self.collection.count()} itens.")
            return

        df = pd.read_csv(CSV_PATH)
        ids, documents, metadatas = [], [], []

        for _, row in df.iterrows():
            raw_code = str(row["Codigo"]).strip()
            description = str(row["Descricao"]).strip()

            code_digits = self.normalize_code(raw_code)
            nivel, codigo_pai = self.classify_ncm(code_digits)

            ids.append(str(uuid.uuid4()))
            documents.append(description)
            metadatas.append({
                "codigo_ncm": code_digits,
                "codigo_ncm_original": raw_code,
                "descricao_original": description,
                "nivel": nivel,
                "codigo_pai": codigo_pai
            })

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Collection populada com {len(df)} itens!")

    def search_ncm(self, query: str) -> Response:
        try:
            query_optimized = formated_query(query)
            results = self.collection.query(
                query_texts=[query_optimized],
                n_results=10  # pega mais candidatos para poder ter 2 pais
            )

            ncm_results = []
            parent_count = 0
            max_parents = 2
            max_children = 1

            for meta, doc, dist in zip(
                results['metadatas'][0],
                results['documents'][0],
                results['distances'][0]
            ):
                codigo = meta['codigo_ncm']
                pai = codigo[:6]

                if parent_count < max_parents:
                    # Adiciona o pai
                    ncm_results.append(NCMResult(
                        ncm_code=chroma_manager.format_ncm(pai),
                        description=doc,
                        distance=dist,
                        is_parent=True
                    ))
                    parent_count += 1

                    # Busca até max_children filhos
                    filhos = self.collection.query(
                        query_texts=[query_optimized],
                        where={"codigo_pai": {"$eq": pai}},
                        n_results=max_children
                    )

                    for f_meta, f_doc, f_dist in zip(
                        filhos['metadatas'][0],
                        filhos['documents'][0],
                        filhos['distances'][0]
                    ):
                        ncm_results.append(NCMResult(
                            ncm_code=chroma_manager.format_ncm(f_meta['codigo_ncm']),
                            description=f_doc,
                            distance=f_dist,
                            is_parent=False
                        ))

            return Response(query=query, results=ncm_results)

        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return Response(query=query, results=[])
chroma_manager = ChromaDBManager()
        