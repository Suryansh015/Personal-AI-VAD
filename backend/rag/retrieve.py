import os
import faiss
import numpy as np

from rag.embed import embed


# backend/rag/retrieve.py → backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_PATH = os.path.join(BACKEND_DIR, "rag", "owner.index")
DOCS_PATH = os.path.join(BACKEND_DIR, "rag", "docs.npy")

index = faiss.read_index(INDEX_PATH)
docs = np.load(DOCS_PATH, allow_pickle=True)

def retrieve(query: str, k=3):
    q_vec = embed(query).astype("float32")
    distances, indices = index.search(np.array([q_vec]), k)

    results = []
    for i, d in zip(indices[0], distances[0]):
        if d < 1.5:  # similarity threshold
            results.append(docs[i])

    return results

if __name__ == "__main__":
    test_queries = [
        "What am I working on?",
        "What are my goals?",
        "What is the capital of France?"
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        results = retrieve(q)
        print("Results:")
        for r in results:
            print("-", r[:200], "...")
