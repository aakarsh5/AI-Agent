import os
import base64
from typing import List, Optional
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

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

    # Separate text chunks and image docs
    text_chunks = [doc.page_content for doc in docs if doc.metadata.get("type") != "Image"]
    image_docs = [doc for doc in docs if doc.metadata.get("type") == "Image"]

    context = "\n\n".join(text_chunks)
    content = [{"type": "text", "text": f"Context:\n{context}\n\nQuestion: {question}"}]

    # If image present, add base64-encoded image
    for img_doc in image_docs:
        image_base64 = img_doc.metadata.get("image_base64")
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"}
            })

    messages.append(HumanMessage(content=content))

    # Get response from Gemini
    response = llm.invoke(messages)
    return response.content




if __name__ == "__main__":
    from pdf_parser import output 

    # question = output["question"]
    docs = output["docs"]
    assert isinstance(output["docs"],list)
    assert all(isinstance(doc,Document) for doc in output["docs"])

    print("Ask Your Question. Write quit or exit to exit.")

    while True:
        question = input("Ask Your Question ")
        if question.lower() in ['exit','quit']:
            print("Exiting:")
            break

        answer = ask_question_with_docs(docs, question)
        print("\n Answer:")
        print(answer)