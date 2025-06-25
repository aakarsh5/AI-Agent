import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import subprocess

# Load environment variables (if any)
load_dotenv()

# Initialize local embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Define embedding function compatible with ChromaDB ≥ 0.4.16
class LocalEmbeddingFunction:
    def __call__(self, input):  # Must use 'input' as the argument name
        return embedder.encode(input).tolist()

    def name(self):
        return "local-sentence-transformer"

# Create Chroma client and collection
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "document_collection"
embedding_fn = LocalEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_fn
)

# Define function to call Ollama model
def query_ollama(prompt, model="llama3"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        return f"Error calling Ollama: {e}"

# Your question to the model
question = "What is the capital of Nepal?"

# Prepare prompt
prompt = f"User: {question}\nAssistant:"

# Call Ollama and print the result
response = query_ollama(prompt)

print("\n📍 Answer from Ollama:")
print(response)
