from app.services.execution_orchestrator import run_task

def execute_plan(plan):
    """
    Executes the evolution plan using the execution orchestrator.
    Usually triggers a dev_loop action.
    """
    print(f"⚙️ Executing Evolution Plan: {plan.get('title')}")

    # The phase_planner_service already formats the plan for execution_orchestrator
    # which expects an 'action' field (like 'dev_loop').
    result = run_task(plan)

    return result
