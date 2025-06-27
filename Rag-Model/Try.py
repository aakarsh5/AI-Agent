import os
import getpass
import bs4
from typing_extensions import List, TypedDict

from langchain import hub
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chat_models import init_chat_model
from langgraph.graph import START, StateGraph

# ─── Environment Setup ────────────────────────────────────────────────
os.environ["USER_AGENT"] = "LangChainBot/0.1"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter LangSmith API key: ")

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

# ─── Model Initialization ─────────────────────────────────────────────
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# ─── Load and Chunk Web Content ───────────────────────────────────────
loader = WebBaseLoader(
    web_paths=["https://lilianweng.github.io/posts/2023-06-23-agent/"],
    bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))},
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
splits = text_splitter.split_documents(docs)

# ─── Vector Store ─────────────────────────────────────────────────────
vector_store = InMemoryVectorStore(embeddings)
_ = vector_store.add_documents(splits)

# ─── Prompt and State Definition ──────────────────────────────────────
prompt = hub.pull("rlm/rag-prompt")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# ─── Application Steps ────────────────────────────────────────────────
def retrieve(state: State):
    return {"context": vector_store.similarity_search(state["question"])}

def generate(state: State):
    context_text = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": context_text})
    response = llm.invoke(messages)
    return {"answer": response.content}

# ─── Graph Compilation ────────────────────────────────────────────────
graph = (
    StateGraph(State)
    .add_sequence([retrieve, generate])
    .add_edge(START, "retrieve")
    .compile()
)

# ─── Run ──────────────────────────────────────────────────────────────
response = graph.invoke({"question": "What is Task Decomposition?"})
print(response["answer"])
