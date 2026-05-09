import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from .code_chunker import chunk_code

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

index = None
metadata = []

def build_index(repo_path=None):
    if repo_path is None:
        repo_path = settings.REPOS_PATH

    global index, metadata

    new_vectors = []
    new_metadata = []

    if not os.path.exists(repo_path):
        return {"chunks": 0, "error": "Repo path does not exist"}

    for root, dirs, files in os.walk(repo_path):
        for f in files:
            if f.endswith(".py") or f.endswith(".js"):
                path = os.path.join(root, f)

                chunks = chunk_code(path)

                for c in chunks:
                    emb = MODEL.encode(c["content"])
                    new_vectors.append(emb)
                    new_metadata.append(c)

    if not new_vectors:
        return {"chunks": 0}

    vectors_np = np.array(new_vectors).astype("float32")
    dim = vectors_np.shape[1]

    new_index = faiss.IndexFlatL2(dim)
    new_index.add(vectors_np)

    index = new_index
    metadata = new_metadata

    return {"chunks": len(metadata)}
