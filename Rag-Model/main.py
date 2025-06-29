from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from ask_llm import run_pdf_pipeline
from qa_engine import ask_question_with_docs

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store docs in memory or cache (you can persist to Redis later)
pdf_docs_cache = {}

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run PDF parsing pipeline
    docs = run_pdf_pipeline(file_path)

    # Cache the docs with file ID
    pdf_docs_cache[file_id] = docs

    return {"message": "PDF processed successfully", "file_id": file_id}

@app.post("/ask")
async def ask_question(file_id: str = Form(...), question: str = Form(...)):
    docs = pdf_docs_cache.get(file_id)

    if not docs:
        return JSONResponse(status_code=404, content={"error": "File not found or not processed yet."})

    answer = ask_question_with_docs(docs, question)
    return {"answer": answer}
