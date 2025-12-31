import os
import numpy as np
import faiss

from rag.embed import embed


# backend/rag/ingest.py → backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BACKEND_DIR, "data")
INDEX_PATH = os.path.join(BACKEND_DIR, "rag", "owner.index")
DOCS_PATH = os.path.join(BACKEND_DIR, "rag", "docs.npy")

CHUNK_SIZE = 400
OVERLAP = 50

def chunk_text(text):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return chunks

def ingest():
    documents = []

    for file in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()
            documents.extend(chunk_text(text))

    vectors = np.array([embed(doc) for doc in documents]).astype("float32")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, INDEX_PATH)
    np.save(DOCS_PATH, documents)

    print(f"Ingested {len(documents)} chunks")

if __name__ == "__main__":
    ingest()
