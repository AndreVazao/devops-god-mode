def create_plan(decisions):
    plan = []

    for d in decisions:
        if d["action"] == "fix_errors":
            plan.append("Run diagnostics and fix failing modules")

        elif d["action"] == "reuse_code":
            plan.append("Search and reuse existing components")

        elif d["action"] == "improve_architecture":
            plan.append("Refactor architecture for scalability")

    return plan
