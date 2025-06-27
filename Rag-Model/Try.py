import os
import bs4
from dotenv import load_dotenv
from typing_extensions import List, TypedDict

from langchain import hub
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chat_models import init_chat_model
from langgraph.graph import START, StateGraph

# ─── Load Environment Variables ───────────────────────────────────────
load_dotenv()

# ─── Initialize Models ────────────────────────────────────────────────
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

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

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
if __name__ == "__main__":
    question = "What is Task Decomposition?"
    response = graph.invoke({"question": question})
    print(f"\n🧠 Answer:\n{response['answer']}")
    
print(f"Split blog post into {len(all_splits)} sub-documents.")

example_message = prompt.invoke(
    {"context":"Summary","question":"What is the capital of Nepal?"}
).to_messages()

assert len(example_message) == 1
print(example_message[0].content)
