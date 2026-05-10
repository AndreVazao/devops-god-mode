def decide(memory, insights):
    decisions = []

    if "erro" in str(memory).lower() or "error" in str(memory).lower():
        decisions.append({
            "priority": 1,
            "action": "fix_errors"
        })

    if len(insights) > 0:
        decisions.append({
            "priority": 2,
            "action": "reuse_code"
        })

    decisions.append({
        "priority": 3,
        "action": "improve_architecture"
    })

    decisions.sort(key=lambda x: x["priority"])

    return decisions
