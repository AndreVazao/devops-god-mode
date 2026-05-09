def suggest_architecture(context: list[str]):
    suggestions = []

    context_str = " ".join(context).lower()

    if "mobile" in context_str:
        suggestions.append("use relay pattern")

    if "executor" in context_str:
        suggestions.append("use local_executor_service")

    if "multi-repo" in context_str or "cross-repo" in context_str:
        suggestions.append("use shared pattern library")

    return suggestions
