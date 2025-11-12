# Import Langchain modules
import uuid
import requests
from typing import List
from langchain.embeddings.base import Embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma
import streamlit as st  
import pandas as pd


embedding = 'qwen3-embedding:0.6b'


loader_invoice = PyPDFLoader("app/libs/extract_pdf/extract_new/INVOICE TECSYS.pdf")
pages_invoice = loader_invoice.load()
print(pages_invoice)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=50,
    length_function=len,
    separators=["\n", "PN:", " - ", ":", "  ", " ", ""]
)

chunks = text_splitter.split_documents(pages_invoice)


class CustomOllamaEmbeddingFunction(Embeddings):
    def __init__(self, model_name: str, url: str = "http://localhost:11434", timeout: int = 120):
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
        response = requests.post(
            f"{self.url}/api/embeddings",
            json={"model": self.model_name, "prompt": text},
            timeout=self.timeout
        )
        if response.status_code == 200:
            return response.json().get('embedding', [])
        return []

embedding_function = CustomOllamaEmbeddingFunction("nomic-embed-text")


def create_vectorstore(chunks, embedding_function, vectorstore_path):

    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
    
    unique_ids = set()
    unique_chunks = []
    
    unique_chunks = [] 
    for chunk, id in zip(chunks, ids):     
        if id not in unique_ids:       
            unique_ids.add(id)
            unique_chunks.append(chunk) 

    vectorstore = Chroma.from_documents(documents=unique_chunks, 
                                        ids=list(unique_ids),
                                        embedding=embedding_function, 
                                        persist_directory = vectorstore_path)

    vectorstore.persist()
    
    return vectorstore


vectorstore = create_vectorstore(chunks=chunks, 
                                 embedding_function=embedding_function, 
                                 vectorstore_path="vectorstore2_invoice")

vectorstore = Chroma(persist_directory="vectorstore2_invoice", embedding_function=embedding_function)


retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20} 
)
    
relevant_chunks = retriever.invoke("PN:")

lis = []

for i, doc in enumerate(relevant_chunks):
    lis.append(doc.page_content)


print(lis)