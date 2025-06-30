from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
import shutil

from pdf_parser import parse_pdf_and_return_docs as parse_pdf
from ask_llm import ask_question_with_docs
from langchain_core.documents import Document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

doc_store = {}
UPLOAD_DIR = "./uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), question: str = Form(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        docs = parse_pdf(file_path)
        doc_store[file_id] = docs

        answer = ask_question_with_docs(docs, question)
        return {"file_id": file_id, "answer": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask/")
async def ask_question(file_id: str = Form(...), question: str = Form(...)):
    docs = doc_store.get(file_id)
    if not docs:
        return JSONResponse(status_code=404, content={"error": "File ID not found."})
    answer = ask_question_with_docs(docs, question)
    return {"answer": answer}
