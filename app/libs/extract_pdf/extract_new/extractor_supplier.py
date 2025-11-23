import uuid
from typing import List
from pathlib import Path

from langchain_community.document_loaders.pdf import PyPDFLoader #type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter #type: ignore
from langchain.embeddings.base import Embeddings #type: ignore
from langchain_community.vectorstores import Chroma #type: ignore

from app.log.logger import logger
from app.libs.extract_pdf.extract_new.extract_supplier import extract_supplier, SupplierInfo


# Caminhos base (ajusta o PDF aqui quando quiser testar outro)
BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "exemplo_pdf_entrada.pdf"
VECTORSTORE_PATH = BASE_DIR / "vectorstore_supplier"

# Modelo de embedding do Ollama (apenas para debug com Chroma, se quiser)
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
OLLAMA_URL = "http://localhost:11434"
TIMEOUT = 120


class CustomOllamaEmbeddingFunction(Embeddings):
    def __init__(self, model_name: str, url: str = OLLAMA_URL, timeout: int = TIMEOUT):
        self.model_name = model_name
        self.url = url
        self.timeout = timeout

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import requests

        vectors: List[List[float]] = []
        for text in texts:
            if not text or not text.strip():
                vectors.append([0.0] * 768)
                continue

            try:
                resp = requests.post(
                    f"{self.url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                emb = resp.json().get("embedding", [])
                if not emb:
                    emb = [0.0] * 768
                vectors.append(emb)
            except Exception as e:
                logger.error(f"[EMBEDDING] Error: {e}")
                vectors.append([0.0] * 768)

        return vectors

    def embed_query(self, text: str) -> List[float]:
        import requests

        try:
            resp = requests.post(
                f"{self.url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            emb = resp.json().get("embedding", [])
            if not emb:
                emb = [0.0] * 768
            return emb
        except Exception as e:
            logger.error(f"[EMBEDDING] Error: {e}")
            return [0.0] * 768


class SupplierChromaManager:
    def __init__(self):
        logger.info("[CHROMADB-SUPPLIER] Initializing")
        self.embedding_function = CustomOllamaEmbeddingFunction(EMBEDDING_MODEL)
        self.vectorstore = self._load_or_create_vectorstore()
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10},
        )

        # texto completo do PDF (para o extractor de supplier)
        pages = PyPDFLoader(str(PDF_PATH)).load()
        self.full_text = "\n\n".join(doc.page_content for doc in pages)

        logger.info("[CHROMADB-SUPPLIER] Ready")

    def _load_or_create_vectorstore(self):
        try:
            store = Chroma(
                persist_directory=str(VECTORSTORE_PATH),
                embedding_function=self.embedding_function,
            )
            if store._collection.count() > 0:
                logger.info(f"[CHROMADB-SUPPLIER] Loaded with {store._collection.count()} documents")
                return store
        except Exception as e:
            logger.warning(f"[CHROMADB-SUPPLIER] Failed to load: {e}")

        return self._create_vectorstore_from_pdf(PDF_PATH)

    def _create_vectorstore_from_pdf(self, path: Path):
        logger.info(f"[CHROMADB-SUPPLIER] Creating new store from: {path}")

        pages = PyPDFLoader(str(path)).load()
        logger.info(f"[CHROMADB-SUPPLIER] Loaded {len(pages)} pages")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            length_function=len,
            separators=["\n\n", "\n", "\t"],
        )

        chunks = splitter.split_documents(pages)
        logger.info(f"[CHROMADB-SUPPLIER] Produced {len(chunks)} chunks")

        unique = {}
        for doc in chunks:
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content))
            unique[uid] = doc.page_content

        ids = list(unique.keys())
        texts = list(unique.values())

        logger.info(f"[CHROMADB-SUPPLIER] Deduplicated to {len(texts)} chunks")

        store = Chroma(
            persist_directory=str(VECTORSTORE_PATH),
            embedding_function=self.embedding_function,
        )
        store.add_texts(texts=texts, ids=ids)

        logger.info("[CHROMADB-SUPPLIER] Store created and populated")
        return store

    def search_chunks(self, query: str) -> List[str]:
        try:
            logger.info(f"[CHROMADB-SUPPLIER] Searching: {query}")
            docs = self.retriever.invoke(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"[CHROMADB-SUPPLIER] Search error: {e}")
            return []


if __name__ == "__main__":
    manager = SupplierChromaManager()

    print("=== CHUNKS RELEVANTES (debug) ===")
    for q in ["Mouser", "Avnet", "XWORK", "TECSYS", "Electronics"]:
        parts = manager.search_chunks(q)
        if not parts:
            continue
        print(f"\n--- Query: {q} ---")
        for i, part in enumerate(parts, 1):
            print(f"\n[{i}] ----------------------------")
            print(part)

    print("\n=== SUPPLIER INFO EXTRAÍDO DO PDF ===\n")
    info: SupplierInfo = extract_supplier(manager.full_text)
    print(f"supplier_name: {info.supplier_name}")
    print(f"supplier_address: {info.supplier_address}")
    print(f"supplier_email: {info.supplier_email}")
    print(f"supplier_phone: {info.supplier_phone}")
