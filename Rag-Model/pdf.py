from typing import TypedDict, List, Literal, Optional
from langchain_core.documents import Document
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
    retu




