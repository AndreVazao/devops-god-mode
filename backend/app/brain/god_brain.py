from app.evolution.memory_reader import read_memory
from app.semantic.project_intelligence import analyze_project
from app.semantic.decision_engine import decide
from app.semantic.execution_planner import create_plan
from app.brain.auto_dev_elite import auto_dev
from app.brain.pipeline import pipeline
from app.brain.agents.core.orchestrator import run_task

def think(goal, chatId="global"):
    # 1. Read Project Memory
    memory = read_memory()

    # 2. Analyze Projects based on the goal
    insights = analyze_project(goal)

    # 3. Use the new Distributed Agent Orchestrator for complex tasks
    print(f"🧠 [God Brain] Thinking about: {goal}")

    # Routing to Pipeline/Agents for creation/build tasks
    if any(kw in goal.lower() for kw in ["criar", "build", "projeto", "app"]):
        print("🚀 [God Brain] Routing to Distributed Agent Orchestrator...")
        # We can run orchestrator which decomposition and execution
        result = run_task(goal, chatId=chatId)
        return {
            "goal": goal,
            "status": result.get("status"),
            "plan": [s["task"] for s in result.get("steps", [])],
            "summary": result.get("summary"),
            "steps": result.get("steps"),
            "distributed": True
        }

    # Pipeline Integration Phase 234 (Fallback for other create tasks)
    if any(kw in goal.lower() for kw in ["deploy"]):
        print("🚀 [God Brain] Routing to Pipeline...")
        return pipeline(goal)

    # Decidimos se usamos o fluxo elite ou o fluxo legado
    if len(goal.split()) > 3 or any(kw in goal.lower() for kw in ["fix", "erro"]):
        print("🚀 [God Brain] Routing to Auto-Dev Elite...")
        result = auto_dev(goal, chatId=chatId)

        return {
            "goal": goal,
            "status": result.get("status"),
            "plan": result.get("plan"),
            "summary": result.get("summary"),
            "source": result.get("source"),
            "results": result.get("results"),
            "elite": True
        }

    # 4. Fallback/Legacy decisions
    decisions = decide(memory, insights)
    plan = create_plan(decisions)

    return {
        "goal": goal,
        "insights": insights,
        "decisions": decisions,
        "plan": plan,
        "elite": False
    }
