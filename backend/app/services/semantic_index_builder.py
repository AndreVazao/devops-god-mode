import os
import logging

logger = logging.getLogger(__name__)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    logger.warning("FAISS not found. Semantic search fallback mode enabled.")
    HAS_FAISS = False

np = None
HAS_NUMPY = False
_NUMPY_ATTEMPTED = False

MODEL = None
HAS_TRANSFORMERS = False
_TRANSFORMER_LOAD_ATTEMPTED = False


def _ensure_numpy():
    global np, HAS_NUMPY, _NUMPY_ATTEMPTED
    if _NUMPY_ATTEMPTED:
        return HAS_NUMPY
    _NUMPY_ATTEMPTED = True
    try:
        import numpy as _np
        np = _np
        HAS_NUMPY = True
        logger.info("NumPy loaded for semantic index builder.")
    except Exception as e:
        logger.warning("NumPy not available or failed to load for semantic index builder. FAISS indexing disabled. %s", e)
        np = None
        HAS_NUMPY = False
    return HAS_NUMPY


def _load_transformer_model():
    global MODEL, HAS_TRANSFORMERS, _TRANSFORMER_LOAD_ATTEMPTED
    if _TRANSFORMER_LOAD_ATTEMPTED:
        return MODEL
    _TRANSFORMER_LOAD_ATTEMPTED = True
    try:
        from sentence_transformers import SentenceTransformer
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        HAS_TRANSFORMERS = True
        logger.info("SentenceTransformers model loaded for semantic indexing.")
    except Exception as e:
        logger.warning(f"SentenceTransformers failed to load: {e}. Embedding disabled.")
        HAS_TRANSFORMERS = False
        MODEL = None
    return MODEL

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
                    if MODEL is None and not _TRANSFORMER_LOAD_ATTEMPTED:
                        _load_transformer_model()
                    for c in chunks:
                        if HAS_TRANSFORMERS and MODEL:
                            emb = MODEL.encode(c["content"])
                            new_vectors.append(emb)
                        new_metadata.append(c)
                except Exception as e:
                    logger.error(f"Error chunking {path}: {e}")

    if not new_metadata:
        return {"chunks": 0}

    if HAS_FAISS and _ensure_numpy() and new_vectors:
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
