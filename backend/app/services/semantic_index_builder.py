import os
import logging

logger = logging.getLogger(__name__)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    logger.warning("FAISS not found. Semantic search fallback mode enabled.")
    HAS_FAISS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    logger.warning("NumPy not found. Semantic search fallback mode enabled.")
    HAS_NUMPY = False

try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_TRANSFORMERS = True
except Exception as e:
    logger.warning(f"SentenceTransformers failed to load: {e}. Embedding disabled.")
    HAS_TRANSFORMERS = False
    MODEL = None

from app.config import settings
from .code_chunker import chunk_code

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

                try:
                    chunks = chunk_code(path)
                    for c in chunks:
                        if HAS_TRANSFORMERS and MODEL:
                            emb = MODEL.encode(c["content"])
                            new_vectors.append(emb)
                        new_metadata.append(c)
                except Exception as e:
                    logger.error(f"Error chunking {path}: {e}")

    if not new_metadata:
        return {"chunks": 0}

    if HAS_FAISS and HAS_NUMPY and new_vectors:
        try:
            vectors_np = np.array(new_vectors).astype("float32")
            dim = vectors_np.shape[1]
            new_index = faiss.IndexFlatL2(dim)
            new_index.add(vectors_np)
            index = new_index
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            index = None
    else:
        index = None

    metadata = new_metadata
    return {"chunks": len(metadata)}
