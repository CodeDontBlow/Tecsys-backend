import uuid
import requests
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma
import streamlit as st
import pandas as pd
from app.log.logger import logger

VECTORSTORE_PATH = "app/libs/extract_pdf/extract_new/vectorstore2_invoice"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434"
TIMEOUT = 120
PDF_PATH = "app/libs/extract_pdf/extract_new/INVOICE TECSYS.pdf"


class CustomOllamaEmbeddingFunction(Embeddings):
    def __init__(self, model_name: str, url: str = OLLAMA_URL, timeout: int = TIMEOUT):
        self.model_name = model_name
        self.url = url
        self.timeout = timeout

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._request_embedding(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._request_embedding(text)

    def _request_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{self.url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
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
            search_kwargs={"k": 20}
        )
        logger.info("[CHROMADB-PDF] Ready")

    def _load_or_create_vectorstore(self):
        try:
            store = Chroma(
                persist_directory=VECTORSTORE_PATH,
                embedding_function=self.embedding_function
            )
            if store._collection.count() > 0:
                logger.info(f"[CHROMADB-PDF] Loaded with {store._collection.count()} documents")
                return store
        except Exception as e:
            logger.warning(f"[CHROMADB-PDF] Failed to load: {e}")

        return self._create_vectorstore_from_pdf(PDF_PATH)

    def _create_vectorstore_from_pdf(self, path: str):
        logger.info("[CHROMADB-PDF] Creating new store")

        pages = PyPDFLoader(path).load()
        logger.info(f"[CHROMADB-PDF] Loaded {len(pages)} pages")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=150,
            chunk_overlap=50,
            length_function=len,
            separators=["\n", "PN:", " - ", ":", "  ", " ", ""]
        )
        chunks = splitter.split_documents(pages)

        logger.info(f"[CHROMADB-PDF] Produced {len(chunks)} chunks")

        unique = {}
        for doc in chunks:
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content))
            if uid not in unique:
                unique[uid] = doc

        logger.info(f"[CHROMADB-PDF] Deduplicated to {len(unique)} chunks")

        store = Chroma.from_documents(
            documents=list(unique.values()),
            ids=list(unique.keys()),
            embedding=self.embedding_function,
            persist_directory=VECTORSTORE_PATH
        )
        store.persist()
        logger.info("[CHROMADB-PDF] Store created")

        return store

    def search_parts(self, query: str = "PN:") -> List[str]:
        try:
            logger.info(f"[CHROMADB-PDF] Searching: {query}")
            docs = self.retriever.invoke(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"[CHROMADB-PDF] Search error: {e}")
            return []


invoice_chroma_manager = InvoiceChromaDBManager()

if __name__ == "__main__":
    results = invoice_chroma_manager.search_parts("PN:")
    print("Relevant Parts Found:")
    for i, part in enumerate(results, 1):
        print(f"{i}. {part}")
