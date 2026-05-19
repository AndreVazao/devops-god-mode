import os
import json
import logging

logger = logging.getLogger(__name__)

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
        logger.info("NumPy loaded for semantic brain.")
    except Exception as e:
        logger.warning("NumPy not available or failed to load for semantic brain. Falling back to pure-Python operations. %s", e)
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
        logger.info("SentenceTransformers model loaded for semantic brain.")
    except Exception as e:
        logger.warning(f"SentenceTransformers failed to load: {e}. Embedding disabled.")
        HAS_TRANSFORMERS = False
        MODEL = None
    return MODEL

from app.config import settings

INDEX_DIR = settings.SEMANTIC_INDEX_PATH
INDEX_FILE = os.path.join(INDEX_DIR, "index.json")

def dot_product(v1, v2):
    """Pure Python dot product fallback."""
    return sum(x * y for x, y in zip(v1, v2))

def embed(text):
    if MODEL is None and not _TRANSFORMER_LOAD_ATTEMPTED:
        _load_transformer_model()
    if HAS_TRANSFORMERS and MODEL:
        try:
            return MODEL.encode(text).tolist()
        except Exception as e:
            logger.warning(f"Embedding failed: {e}. Using fallback vector.")
    return [0.0] * 384  # Dummy vector if embedding is disabled

def load_index():
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_index(data):
    os.makedirs(INDEX_DIR, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f)

def add_to_index(file_path, content):
    index = load_index()
    add_many_to_index(index, [(file_path, content)])
    save_index(index)

def add_many_to_index(index, items):
    """
    items: list of (file_path, content) tuples
    """
    for file_path, content in items:
        vector = embed(content[:2000])
        index.append({
            "file": file_path,
            "content": content[:2000],
            "vector": vector
        })

def search(query, top_k=5):
    index = load_index()
    if not index:
        return []

    q_vec_list = embed(query)

    results = []

    for item in index:
        item_vec = item.get("vector", [])
        if not item_vec:
            continue

        if _ensure_numpy():
            try:
                score = float(np.dot(np.array(q_vec_list), np.array(item_vec)))
            except Exception:
                score = dot_product(q_vec_list, item_vec)
        else:
            score = dot_product(q_vec_list, item_vec)

        results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:top_k]]
