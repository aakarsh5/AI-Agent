# vector_store.py

from typing import Dict
from langchain_core.documents import Document

# In-memory store: { file_id: List[Document] }
store: Dict[str, list] = {}

def save_docs(file_id: str, docs: list):
    store[file_id] = docs

def get_docs(file_id: str):
    return store.get(file_id)
