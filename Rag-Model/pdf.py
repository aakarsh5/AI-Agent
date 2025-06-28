from typing import TypedDict, List, Literal, Optional
from langchain_core.documents import Document
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
import fitz  # PyMuPDF
import base64
import io
from PIL import Image
import os


# Define the workflow state
class State(TypedDict):
    question: str
    query_type: Literal["text", "visual"]
    query: dict
    answer: Optional[str]

    pdf_path: str
    current_page: int
    total_pages: int
    page_docs: List[Document]
    docs: List[Document]
    page_image: Optional[str]


# Load and classify page
def extract_page_content(state: State):
    loader = UnstructuredLoader(
        file_path=state["pdf_path"],
        strategy="hi_res",
        partition_via_api=False,
    )
    all_docs = list(loader.lazy_load())
    page_docs = [doc for doc in all_docs if doc.metadata.get("page_number") == state["current_page"]]
    return {"page_docs": page_docs}


# Determine if page is image-based
def is_image_page(state: State):
    if not state["page_docs"]:
        return True
    return any(doc.metadata.get("category") == "Image" for doc in state["page_docs"])


# Process text page
def process_text_page(state: State):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(state["page_docs"])
    return {"docs": state["docs"] + chunks}


# Process image page
def process_image_page(state: State):
    doc = fitz.open(state["pdf_path"])
    page = doc.load_page(state["current_page"] - 1)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    image_doc = Document(
        page_content="base64:image",
        metadata={
            "page_number": state["current_page"],
            "image_base64": encoded,
            "type": "Image"
        },
    )
    return {"docs": state["docs"] + [image_doc]}


# Advance page
def advance_page(state: State):
    return {"current_page": state["current_page"] + 1}


# Gemini LLM setup
llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")


# Final QA step using Gemini
def query_llm(state: State):
    if state["query_type"] == "visual":
        image_docs = [doc for doc in state["docs"] if doc.metadata.get("type") == "Image"]
        if not image_docs:
            return {"answer": "No image found to analyze."}
        image_base64 = image_docs[0].metadata["image_base64"]
        response = llm.invoke([
            f"Question: {state['question']}",
            {"image": image_base64}
        ])
        return {"answer": response.text}
    else:
        text = "\n".join([doc.page_content for doc in state["docs"]])
        response = llm.invoke(f"Question: {state['question']}\n\n{text}")
        return {"answer": response.text}


# Build the LangGraph workflow
graph = StateGraph(State)
graph.add_node("extract", extract_page_content)
graph.add_node("text_handler", process_text_page)
graph.add_node("image_handler", process_image_page)
graph.add_node("advance", advance_page)
graph.add_node("query_llm", query_llm)

graph.set_entry_point("extract")

graph.add_conditional_edges("extract", is_image_page, {
    True: "image_handler",
    False: "text_handler"
})

graph.add_edge("text_handler", "advance")
graph.add_edge("image_handler", "advance")

graph.add_conditional_edges("advance", lambda s: s["current_page"] <= s["total_pages"], {
    True: "extract",
    False: "query_llm"
})

graph.set_finish_point("query_llm")
compiled = graph.compile()


# Run the pipeline
if __name__ == "__main__":
    pdf_path = "./hello.pdf"  # File is in the same folder

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output = compiled.invoke({
        "question": "What does the diagram on page 4 explain?",
        "query_type": "visual",  # or "text"
        "query": {},
        "answer": None,
        "pdf_path": pdf_path,
        "current_page": 1,
        "total_pages": 16,
        "page_docs": [],
        "docs": [],
        "page_image": None
    })

    print("\n✅ Gemini's Answer:")
    print(output["answer"])
