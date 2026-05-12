from app.evolution.memory_reader import read_memory
from app.semantic.project_intelligence import analyze_project
from app.semantic.decision_engine import decide
from app.semantic.execution_planner import create_plan
from app.brain.auto_dev_elite import auto_dev
from app.brain.pipeline import pipeline

def think(goal, chatId="global"):
    # 1. Read Project Memory
    memory = read_memory()

    # 2. Analyze Projects based on the goal
    insights = analyze_project(goal)

    # 3. Use the new Auto-Dev Elite loop for complex tasks
    print(f"🧠 [God Brain] Thinking about: {goal}")

    # Pipeline Integration Phase 234
    if any(kw in goal.lower() for kw in ["criar", "build"]):
        print("🚀 [God Brain] Routing to Pipeline...")
        return pipeline(goal)

    # Decidimos se usamos o fluxo elite ou o fluxo legado
    if len(goal.split()) > 3 or any(kw in goal.lower() for kw in ["fix", "deploy", "erro"]):
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
