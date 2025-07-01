### 🧠 ask_llm.py
import os
import uuid
import time
import fitz
import shutil
import threading
from typing import List
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from pdf_parser import run_pdf_pipeline

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")
EMBEDDINGS = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
TEMP_STORE = {}

# Step 1: Store Docs

def store_pdf_in_chroma(docs: List[Document], namespace: str) -> Chroma:
    cleaned_docs = []
    for doc in docs:
        if isinstance(doc, Document):
            cleaned_doc = filter_complex_metadata(doc)
            cleaned_docs.append(cleaned_doc)
        else:
            print(f"[WARN] Skipping non-Document entry: {type(doc)}")

    persist_path = f"./tmp_store/{namespace}"
    if os.path.exists(persist_path):
        shutil.rmtree(persist_path)

    vectorstore = Chroma.from_documents(
        documents=cleaned_docs,
        embedding=EMBEDDINGS,
        persist_directory=persist_path
    )
    TEMP_STORE[namespace] = persist_path
    return vectorstore

# Step 2: Ask Questions

def ask_question_from_chroma(question: str, vectorstore: Chroma) -> str:
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )
    return qa_chain.run(question)

# Step 3: Auto delete after timeout

def schedule_deletion(namespace: str, timeout: int = 600):
    def delete_after():
        time.sleep(timeout)
        path = TEMP_STORE.pop(namespace, None)
        if path and os.path.exists(path):
            shutil.rmtree(path)
            print(f"[INFO] Deleted vectorstore at: {path}")
    threading.Thread(target=delete_after, daemon=True).start()

# Step 4: Run the full flow

if __name__ == "__main__":
    pdf_path = "./hello.pdf"
    total_pages = len(fitz.open(pdf_path))
    first_question = input("Enter your Question? ")

    namespace = str(uuid.uuid4())[:8]

    output = run_pdf_pipeline({
        "question": first_question,
        "query_type": "visual",
        "query": {},
        "answer": None,
        "pdf_path": pdf_path,
        "current_page": 1,
        "total_pages": total_pages,
        "page_docs": [],
        "docs": [],
        "page_image": None
    })

    docs = output["docs"]
    vectorstore = store_pdf_in_chroma(docs, namespace)
    schedule_deletion(namespace)

    print("\n✅ You can now ask multiple questions about this PDF. Type 'exit' to quit.\n")
    while True:
        user_q = input("Q: ")
        if user_q.lower() == "exit":
            break
        answer = ask_question_from_chroma(user_q, vectorstore)
        print("A:", answer)

    print("\n[Session Ended]")
