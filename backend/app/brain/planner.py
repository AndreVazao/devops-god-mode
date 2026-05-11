from app.services.goal_planner_service import goal_planner_service

def create_plan(task: str):
    """
    Creates an execution plan using the native God Mode goal planner.
    Returns (steps, plan_source)
    """
    plan = goal_planner_service.create_plan(goal=task)

    # Extract step titles from the generated tasks
    steps = [t["title"] for t in plan.get("tasks", [])]

    return steps, "goal_planner_service"
