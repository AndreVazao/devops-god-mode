from app.brain.agents.core.base_agent import BaseAgent
from app.brain.multi_ai import run_parallel
from app.brain.aggregator import aggregate

class BackendPythonAgent(BaseAgent):
    name = "Python Agent"
    role = "backend"

    def run(self, task, context=None):
        prompt = f"Cria backend em Python (FastAPI ou Flask): {task}\nContexto: {context}"
        results = run_parallel(prompt)
        return aggregate(results)
