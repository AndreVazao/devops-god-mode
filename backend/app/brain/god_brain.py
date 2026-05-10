from app.evolution.memory_reader import read_memory
from app.semantic.project_intelligence import analyze_project
from app.semantic.decision_engine import decide
from app.semantic.execution_planner import create_plan

def think(goal):
    # 1. Read Project Memory
    memory = read_memory()

    # 2. Analyze Projects based on the goal
    insights = analyze_project(goal)

    # 3. Make decisions based on memory and insights
    decisions = decide(memory, insights)

    # 4. Create an execution plan
    plan = create_plan(decisions)

    return {
        "goal": goal,
        "insights": insights,
        "decisions": decisions,
        "plan": plan
    }
