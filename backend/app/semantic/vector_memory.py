from .semantic_brain import add_to_index, search as semantic_search

def add(file_path: str, content: str):
    """
    Adds content to the semantic index.
    """
    add_to_index(file_path, content)

def search(query: str, top_k: int = 5):
    """
    Searches the semantic index and returns a list of content strings.
    """
    results = semantic_search(query, top_k=top_k)
    return [r["content"] for r in results]
