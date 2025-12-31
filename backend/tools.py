# backend/tools.py
from rag.retrieve import retrieve

def search_owner_notes(query: str):
    results = retrieve(query)
    return {
        "matches": results,
        "count": len(results)
    }
