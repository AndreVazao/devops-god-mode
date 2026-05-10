import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_DIR = settings.SEMANTIC_INDEX_PATH
INDEX_FILE = os.path.join(INDEX_DIR, "index.json")

def embed(text):
    return MODEL.encode(text).tolist()

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

    q_vec = np.array(embed(query))

    results = []

    for item in index:
        # Use dot product as requested in prompt
        score = np.dot(q_vec, np.array(item["vector"]))
        results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:top_k]]
