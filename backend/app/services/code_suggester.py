from .semantic_search import search_code

def suggest_code(task_description):
    matches = search_code(task_description)

    suggestions = []

    for m in matches:
        suggestions.append({
            "file": m["file"],
            "snippet": m["content"][:500]
        })

    return suggestions
