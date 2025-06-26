import getpass
import os
import bs4
from langchain import hub # centralized repository
from langchain_community.document_loaders import WebBaseLoader #use to extract and structure and content from web pages
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

##################################################################
#environment variables to start logging traces:
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


###################################################################
# chat model:
if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")



####################################################################
#embeddings model:
if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


######################################################################
#vector store:
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)


#######################################################################
#Load and chunk contents of the blog

loader = WebBaseLoader(
  web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
  bs_kwargs=dict(
    parse_only= bs4.SoupStrainer(
      class_ = ("post-contnet", "post-title", "post-header")
    )
  ),
)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
all_splits = text_splitter.split_documents(docs)

