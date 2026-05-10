from .semantic_brain import search

def analyze_project(goal):
    results = search(goal)

    insights = []

    for r in results:
        insights.append({
            "file": r["file"],
            "hint": r["content"][:200]
        })

    return insights
