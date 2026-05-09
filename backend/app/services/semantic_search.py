from .semantic_index_builder import index, metadata, MODEL
import numpy as np

def search_code(query, top_k=5):
    # Re-import to get the updated global variables from the module
    from . import semantic_index_builder
    idx = semantic_index_builder.index
    meta = semantic_index_builder.metadata

    if idx is None:
        return []

    q_emb = MODEL.encode(query).astype("float32")

    D, I = idx.search(np.array([q_emb]), top_k)

    results = []

    for i in I[0]:
        if 0 <= i < len(meta):
            results.append(meta[i])

    return results
