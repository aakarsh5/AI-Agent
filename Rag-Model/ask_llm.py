import fitz
from typing import List
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pdf_parser import run_pdf_pipeline

# -----------------------------
# Define LLM
# -----------------------------

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")

# -----------------------------
# Answer Question with Text/Image
# -----------------------------

def ask_question_with_docs(docs: List[Document], question: str) -> str:
    messages = [
        SystemMessage(content="You are a helpful assistant who answers questions based on PDF content.")
    ]

    # Separate text and image documents
    text_chunks = [doc.page_content for doc in docs if doc.metadata.get("type") != "Image"]
    image_docs = [doc for doc in docs if doc.metadata.get("type") == "Image"]

    context = "\n\n".join(text_chunks)
    content = [{"type": "text", "text": f"Context:\n{context}\n\nQuestion: {question}"}]

    for img_doc in image_docs:
        image_base64 = img_doc.metadata.get("image_base64")
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"}
            })

    messages.append(HumanMessage(content=content))

    # Get response
    response = llm.invoke(messages)
    return response.content


# -----------------------------
# Main Execution
# -----------------------------

if __name__ == "__main__":
    pdf_path = "./hello.pdf"
    total_pages = len(fitz.open(pdf_path))
    question = input("Enter your Question? ")

    output = run_pdf_pipeline({
        "question": question,
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
    print(f"🔍 Asking: {question}")
    answer = ask_question_with_docs(docs, question)

    print("\n✅ Answer:")
    print(answer)
