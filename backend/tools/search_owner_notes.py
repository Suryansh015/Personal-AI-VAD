from rag.retrieve import retrieve

def search_owner_notes(query: str) -> str:
    results = retrieve(query)

    if not results:
        return "No relevant notes found."

    return "\n".join(results)
