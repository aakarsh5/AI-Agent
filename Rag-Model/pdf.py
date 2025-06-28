from typing import TypedDict, List, Literal, Optional
from langchain_core.documents import Document
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
import fitz
import base64
import io
from PIL import Image



#Define state
class State(TypedDict):
    question:str
    query_type:Literal["text", "visual"]
    query:dict
    answer:Optional[str]

    pdf_path:str
    current_page:int
    total_page:int
    page_docs:List[Document]
    docs:List[Document]
    page_image:Optional[str]


#Load and classify page
def extract_page_content(state:State):
    loader = UnstructuredLoader(
        file_path=state["pdf_path"],
        strategy = "hi_res",j
        partition_vai_api = True,
        coordinates = True,
    )
    all_docs = list(loader.lazy_load())
    page_docs = [doc for doc in all_docs if doc.metadata.get("page_number") == state["current_page"]]
    return {"page_docs":page_docs}

#Determine page type
def is_image_page(state:State):
    return any(doc.metadata.get("category") == "Image" for doc in state["page_docs"])

#Process text page
def process_text_page(state:State):
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    chunks = splitter.split_documents(state["page_docs"])
    return {"docs":state["docs"]+chunks}

#Process image page
def process_image_page(state:State):
    doc = fitz.open(state["pdf_path"])
    page = doc.load_page(state["current_page"]-1)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    image_doc = Document(
        page_content="base64:image",
        metadata={
            "page_number":state["current_page"],
            "image_base64":encoded,
            "type":"Image"
        },
    )
    return {"docs":state["docs"]+ [image_doc]}

# Advance page
def advance_page(state:State):
    return{"currnet_page":state["current_page"]+1}

# Gemini LLM Setup
llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

graph = StateGraph(State)
graph.add_node("extract",extract_page_content)
graph.add_edge("text_handler",process_text_page)
graph.add_edge("image_handler", process_image_page)
graph.add_edge("advance", advance_page)

graph.set_entry_point("extract")

graph.add_conditional_edges("extract",is_image_page,{
    True: "image_handler",
    False: "text_handler"
})

graph.add_edge("text_handler","advance")
graph.add_edge("image_handler", "advance")
graph.add_conditional_edges("advance", lambda s: s["current_page"] <= s["total_pages"],{
    True:"extract",
    False: "__end__"
})

compiled = graph.compile()


output = compiled.invoke({
    "question": "What does the diagram on page 5 explain?",
    "query_type": "visual",
    "query": {},
    "answer": None,
    "pdf_path": "your_file.pdf",
    "current_page": 1,
    "total_pages": 16,
    "page_docs": [],
    "docs": [],
    "page_image": None
})










