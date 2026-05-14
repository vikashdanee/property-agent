# tools/search_lease.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from rag.ingest import search_lease_chunks

class SearchLeaseInput(BaseModel):
    query: str = Field(description="The question to search for in the lease document")

@tool("search_lease", args_schema=SearchLeaseInput)
def search_lease(query: str) -> str:
    """Search the lease agreement document to answer tenant questions.
    Use when a verified resident asks about lease terms, policies, rules,
    fees, pets, parking, noise, utilities, maintenance responsibilities,
    move-out procedures, or anything related to their lease agreement."""
    chunks = search_lease_chunks(query, k=4)
    return f"Relevant lease sections found:\n\n{chunks}"