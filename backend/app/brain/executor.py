from .agent_pool import run_step

def run_plan(plan: list[str]):
    """
    Executes a list of steps sequentially.
    """
    results = []
    print(f"🚀 [Executor] Running plan with {len(plan)} steps")

    for i, step in enumerate(plan):
        print(f"📍 [Executor] Step {i+1}/{len(plan)}: {step}")
        res = run_step(step)
        results.append(res)

        if res.get("status") == "failed":
            print(f"❌ [Executor] Step failed, halting execution.")
            break

    return results
