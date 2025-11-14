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


class CustomOllamaEmbeddingFunction(Embeddings):
    def __init__(self, model_name: str, url: str = OLLAMA_URL, timeout: int = TIMEOUT):
        self.model_name = model_name
        self.url = url
        self.timeout = timeout
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)
    
    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{self.url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get('embedding', [])
        except Exception as e:
            logger.error(f"[EMBEDDING] Error getting embedding: {e}")
            return []


class InvoiceChromaDBManager:
    def __init__(self):
        logger.info("[CHROMADB-PDF] Initializing ChromaDB-PDF client...")
        self.embedding_function = CustomOllamaEmbeddingFunction(EMBEDDING_MODEL)
        self.vectorstore = self._initialize_vectorstore()
        self.retriever = self._create_retriever()
        logger.info("[CHROMADB-PDF] Invoice ChromaDB-PDF initialized successfully")

    def _initialize_vectorstore(self):
        """Initialize or load existing vectorstore"""
        try:
            vectorstore = Chroma(
                persist_directory=VECTORSTORE_PATH,
                embedding_function=self.embedding_function
            )
            if vectorstore._collection.count() > 0:
                logger.info(f"[CHROMADB-PDF] Loaded existing vectorstore with {vectorstore._collection.count()} documents")
                return vectorstore
        except Exception as e:
            logger.warning(f"[CHROMADB-PDF] Could not load existing vectorstore: {e}")

        # Create new vectorstore if doesn't exist
        return self._create_vectorstore_from_pdf()

    def _create_vectorstore_from_pdf(self):
        """Create vectorstore from PDF document"""
        logger.info("[CHROMADB-PDF] Creating new vectorstore from PDF...")
        
        # Load PDF
        loader = PyPDFLoader("app/libs/extract_pdf/extract_new/INVOICE TECSYS.pdf")
        pages = loader.load()
        logger.info(f"[CHROMADB-PDF] Loaded {len(pages)} pages from PDF")

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=150,
            chunk_overlap=50,
            length_function=len,
            separators=["\n", "PN:", " - ", ":", "  ", " ", ""]
        )
        chunks = text_splitter.split_documents(pages)
        logger.info(f"[CHROMADB-PDF] Split into {len(chunks)} chunks")

        # Create unique IDs
        ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
        
        # Remove duplicates
        unique_ids = set()
        unique_chunks = []
        
        for chunk, id in zip(chunks, ids):     
            if id not in unique_ids:       
                unique_ids.add(id)
                unique_chunks.append(chunk)

        logger.info(f"[CHROMADB-PDF] After deduplication: {len(unique_chunks)} chunks")

        # Create vectorstore
        vectorstore = Chroma.from_documents(
            documents=unique_chunks, 
            ids=list(unique_ids),
            embedding=self.embedding_function, 
            persist_directory=VECTORSTORE_PATH
        )
        vectorstore.persist()
        
        logger.info("[CHROMADB-PDF] Vectorstore created and persisted successfully")
        return vectorstore

    def _create_retriever(self, k: int = 20):
        """Create retriever with similarity search"""
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def search_parts(self, query: str = "PN:") -> List[str]:
        """Search for parts in the invoice documents"""
        try:
            logger.info(f"[CHROMADB-PDF] Searching for: {query}")
            relevant_chunks = self.retriever.invoke(query)
            
            results = []
            for i, doc in enumerate(relevant_chunks):
                results.append(doc.page_content)
            
            logger.info(f"[CHROMADB-PDF] Search completed with {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"[CHROMADB-PDF] Error in search_parts: {e}")
            return []


invoice_chroma_manager = InvoiceChromaDBManager()

if __name__ == "__main__":
    relevant_parts = invoice_chroma_manager.search_parts("PN:")
    print("Relevant Parts Found:")
    for i, part in enumerate(relevant_parts):
        print(f"{i+1}. {part}")