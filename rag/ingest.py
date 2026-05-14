# rag/ingest.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = "rag/chroma_db"
LEASE_PDF   = "data/sample_lease.pdf"

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name     = "lease_documents",
        metadata = {"hnsw:space": "cosine"}
    )

def ingest_lease(pdf_path: str = LEASE_PDF):
    """Load PDF, split into chunks, store in ChromaDB."""
    print(f"Loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    pages  = loader.load()
    print(f"Loaded {len(pages)} pages.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size    = 500,
        chunk_overlap = 50,
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks.")

    collection = get_collection()

    # Add documents — ChromaDB uses its own built-in embeddings
    collection.add(
        documents = [c.page_content for c in chunks],
        ids       = [f"chunk_{i}" for i in range(len(chunks))],
        metadatas = [{"source": pdf_path, "page": c.metadata.get("page", 0)}
                     for c in chunks]
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_PATH}")

def search_lease_chunks(query: str, k: int = 4) -> str:
    """Search lease document for relevant chunks."""
    collection = get_collection()
    results    = collection.query(
        query_texts = [query],
        n_results   = k,
    )
    docs = results.get("documents", [[]])[0]
    if not docs:
        return "No relevant information found in the lease document."
    return "\n\n".join(
        [f"[Excerpt {i+1}]\n{doc}" for i, doc in enumerate(docs)]
    )

if __name__ == "__main__":
    ingest_lease()