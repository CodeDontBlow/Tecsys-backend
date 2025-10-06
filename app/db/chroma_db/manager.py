from app.db.chroma_db.config import CHROMA_DB_PATH, COLLECTION_NAME, CSV_PATH
from app.db.chroma_db.embedding import get_embedding_ollama
from app.util.tipi.table_tipi import formated_query
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
        if len(code) == 6:
            return "parent", ""
        elif len(code) == 8:
            return "child", code[:6]  
        return "unknown", ""
    
    def format_ncm(self, code: str) -> str:
        code = code.strip()
        if len(code) == 6:  
            return f"{code[:2]}{code[2:4]}.{code[4:]}"
        elif len(code) == 8:
            return f"{code[:2]}{code[2:4]}.{code[4:6]}.{code[6:]}"
        return code

    def populate_from_csv(self, batch_size: int = 50):
        if self.collection.count() > 0:
            logger.info(f"Collection already has {self.collection.count()} items.")
            return

        df = pd.read_csv(CSV_PATH)
        total_items = len(df)
        logger.info(f"Preparing to add {total_items} items in batches of {batch_size}.")


        ids_batch, documents_batch, metadatas_batch = [], [], []

        for idx, row in df.iterrows():
            raw_code = str(row["ncm"]).strip()
            description = str(row["descrição"]).strip()
            aliquot = str(row.get("alíquota (%)", ""))

            code_digits = self.normalize_code(raw_code)

            if len(code_digits) < 6:
                continue
            level, code_father = self.classify_ncm(code_digits)

            ids_batch.append(str(uuid.uuid4()))
            documents_batch.append(description)
            metadatas_batch.append({
                "code_ncm": code_digits,
                "description": description,
                "level": level,
                "aliquot": aliquot,
                "code_father": code_father
            })

            if len(ids_batch) >= batch_size:
                self._add_batch(ids_batch, documents_batch, metadatas_batch)
                ids_batch, documents_batch, metadatas_batch = [], [], []

        if ids_batch:
            self._add_batch(ids_batch, documents_batch, metadatas_batch)

        logger.info(f"Finished populating {total_items} items into the collection.")

    def _add_batch(self, ids, documents, metadatas):
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added batch of {len(ids)} items.")
        except Exception as e:
            logger.error(f"Error adding batch: {e}")

    def search_ncm(self, query: str) -> Response:
        try:
            query_optimized = formated_query(query)
            print(query_optimized)

            results = self.collection.query(
                query_texts=[query_optimized],
                n_results=50,
                include=['metadatas', 'documents', 'distances']
            )

            ncm_results = []
            seen_parents = set()
            parent_count = 0
            max_parents =3
            max_children = 3

            metas = results['metadatas'][0]
            docs = results['documents'][0]
            dists = results['distances'][0]

            for meta, doc, dist in zip(metas, docs, dists):
                code = meta.get('code_ncm')
                if not code:
                    continue

                parent_code = meta.get('code_father') or (code[:6] if len(code) >= 6 else code)


                if parent_code in seen_parents:
                    continue
                if parent_count >= max_parents:
                    break

                parent_query = self.collection.query(
                    query_texts=[query_optimized],           
                    where={"code_ncm": {"$eq": parent_code}},
                    n_results=1,
                    include=['metadatas', 'documents', 'distances']
                )

                if parent_query['metadatas'][0]:
                    p_meta = parent_query['metadatas'][0][0]
                    p_doc = parent_query['documents'][0][0]
                    p_dist = parent_query['distances'][0][0]
                    p_aliquot = p_meta.get('aliquot')
                    ncm_results.append(NCMResult(
                        ncm_code=self.format_ncm(p_meta['code_ncm']),
                        description=p_doc,
                        distance=p_dist,
                        aliquot=p_aliquot,
                        is_parent=True
                    ))
                else:
                    ncm_results.append(NCMResult(
                        ncm_code=self.format_ncm(parent_code),
                        description=doc,
                        distance=dist,
                        aliquot=meta.get('aliquot'),
                        is_parent=True
                    ))

                parent_count += 1
                seen_parents.add(parent_code)

                childrens = self.collection.query(
                    query_texts=[query_optimized],
                    where={"code_father": {"$eq": parent_code}},
                    n_results=max_children,
                    include=['metadatas', 'documents', 'distances']
                )

                for f_meta, f_doc, f_dist in zip(
                    childrens['metadatas'][0],
                    childrens['documents'][0],
                    childrens['distances'][0]
                ):
                    ncm_results.append(NCMResult(
                        ncm_code=self.format_ncm(f_meta['code_ncm']),
                        description=f_doc,
                        distance=f_dist,
                        aliquot=f_meta.get('aliquot'),
                        is_parent=False
                    ))

            return Response(query=query, results=ncm_results)

        except Exception as e:
            logger.error(f"Error: {e}")
            return Response(query=query, results=[])
        
chroma_manager = ChromaDBManager()