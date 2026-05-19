import logging

logger = logging.getLogger(__name__)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    logger.warning("NumPy not found in semantic_search. Fallback mode enabled.")
    HAS_NUMPY = False

def search_code(query, top_k=5):
    # Re-import to get the updated global variables from the module
    from . import semantic_index_builder
    idx = semantic_index_builder.index
    meta = semantic_index_builder.metadata
    model = semantic_index_builder.MODEL

    if idx is None or model is None or not HAS_NUMPY:
        # Fallback to simple keyword search if metadata exists
        if meta:
            logger.info("Semantic index not available, using keyword fallback.")
            query_lower = query.lower()
            results = [m for m in meta if query_lower in m.get("content", "").lower()]
            return results[:top_k]
        return []

    try:
        q_emb = model.encode(query).astype("float32")
        D, I = idx.search(np.array([q_emb]), top_k)

        results = []
        for i in I[0]:
            if 0 <= i < len(meta):
                results.append(meta[i])
        return results
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return []
