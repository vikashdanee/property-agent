# rag/retriever.py
from langchain_chroma import Chroma
from rag.ingest import search_lease_chunks
import os

def get_retriever(k: int = 4):
    """Get ChromaDB retriever for lease document."""
    embeddings = get_embeddings()
    db = Chroma(
        persist_directory = CHROMA_PATH,
        embedding_function = embeddings,
    )
    return db.as_retriever(search_kwargs={"k": k})

def search_lease_chunks(query: str, k: int = 4) -> str:
    """Search lease document for relevant chunks."""
    retriever = get_retriever(k=k)
    docs      = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the lease document."
    results = []
    for i, doc in enumerate(docs):
        results.append(f"[Excerpt {i+1}]\n{doc.page_content}")
    return "\n\n".join(results)