import uuid
import requests
import re
from typing import List
from pathlib import Path

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma

from app.log.logger import logger  # mantém o seu logger


# Caminhos base (ajusta se quiser)
BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "INVOICE TECSYS.pdf"
VECTORSTORE_PATH = BASE_DIR / "vectorstore2_invoice"

# Modelo de embedding do Ollama
# Use um modelo que você REALMENTE tenha no `ollama list`,
# por exemplo: "qwen3-embedding:0.6b" ou "nomic-embed-text"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"  # troque aqui se quiser
OLLAMA_URL = "http://localhost:11434"
TIMEOUT = 120


class CustomOllamaEmbeddingFunction(Embeddings):
    def __init__(self, model_name: str, url: str = OLLAMA_URL, timeout: int = TIMEOUT):
        self.model_name = model_name
        self.url = url
        self.timeout = timeout

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            if not text or not text.strip():
                # fallback seguro para textos vazios
                vectors.append([0.0] * 768)
                continue

            emb = self._request_embedding(text)
            if not emb:
                # fallback seguro caso o Ollama falhe
                emb = [0.0] * 768

            vectors.append(emb)

        return vectors

    def embed_query(self, text: str) -> List[float]:
        return self._request_embedding(text)

    def _request_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{self.url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=self.timeout,
            )
            response.raise_for_status()
            emb = response.json().get("embedding", [])
            if not emb:
                logger.error(f"[EMBEDDING] Empty embedding returned for text: {text[:80]!r}")
            return emb
        except Exception as e:
            logger.error(f"[EMBEDDING] Error: {e}")
            return []


class InvoiceChromaDBManager:
    def __init__(self):
        logger.info("[CHROMADB-PDF] Initializing")
        self.embedding_function = CustomOllamaEmbeddingFunction(EMBEDDING_MODEL)
        self.vectorstore = self._load_or_create_vectorstore()
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 20},
        )
        logger.info("[CHROMADB-PDF] Ready")

    def _load_or_create_vectorstore(self):
        try:
            store = Chroma(
                persist_directory=str(VECTORSTORE_PATH),
                embedding_function=self.embedding_function,
            )
            if store._collection.count() > 0:
                logger.info(f"[CHROMADB-PDF] Loaded with {store._collection.count()} documents")
                return store
        except Exception as e:
            logger.warning(f"[CHROMADB-PDF] Failed to load: {e}")

        return self._create_vectorstore_from_pdf(PDF_PATH)

    def _create_vectorstore_from_pdf(self, path: Path):
        logger.info(f"[CHROMADB-PDF] Creating new store from: {path}")

        pages = PyPDFLoader(str(path)).load()
        logger.info(f"[CHROMADB-PDF] Loaded {len(pages)} pages")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=150,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", "PN:", " - ", ":", "PN: "],
        )

        chunks = splitter.split_documents(pages)
        logger.info(f"[CHROMADB-PDF] Produced {len(chunks)} chunks")

        # Deduplicar chunks
        unique = {}
        for doc in chunks:
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content))
            unique[uid] = doc.page_content

        ids = list(unique.keys())
        texts = list(unique.values())

        logger.info(f"[CHROMADB-PDF] Deduplicated to {len(texts)} chunks")

        # Criar embedder
        embedder = self.embedding_function

        # Criar banco vazio
        store = Chroma(
            persist_directory=str(VECTORSTORE_PATH),
            embedding_function=embedder,   # AQUI funciona
        )

        # Inserir textos + embeddings
        store.add_texts(texts=texts, ids=ids)

        logger.info("[CHROMADB-PDF] Store created and populated")
        return store

    def search_parts(self, query: str = "PN:") -> List[str]:
        try:
            logger.info(f"[CHROMADB-PDF] Searching: {query}")
            docs = self.retriever.invoke(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"[CHROMADB-PDF] Search error: {e}")
            return []

    def extract_part_numbers(self, query: str = "PN:") -> List[str]:
        texts = self.search_parts(query)

        pn_regex = r"PN[:\s]*([A-Za-z0-9][A-Za-z0-9\-_.]{2,})"   # <<<< AQUI!

        pns: List[str] = []
        for text in texts:
            matches = re.findall(pn_regex, text)
            pns.extend(matches)

        unique = []
        for pn in pns:
            if pn not in unique:
                unique.append(pn)

        return unique



if __name__ == "__main__":
    manager = InvoiceChromaDBManager()

    print("=== CHUNKS RELEVANTES (contendo 'PN:') ===")
    parts = manager.search_parts("PN:")
    for i, part in enumerate(parts, 1):
        print(f"\n[{i}] ----------------------------")
        print(part)

    print("\n=== PART NUMBERS EXTRAÍDOS ===")
    pns = manager.extract_part_numbers("PN:")
    for pn in pns:
        print("-", pn)
