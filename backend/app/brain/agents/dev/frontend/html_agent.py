from app.brain.agents.core.base_agent import BaseAgent
from app.brain.multi_ai import run_parallel
from app.brain.aggregator import aggregate

class FrontendHTMLAgent(BaseAgent):
    name = "HTML Agent"
    role = "frontend"

    def run(self, task, context=None):
        prompt = f"Cria frontend HTML/CSS simples: {task}\nContexto: {context}"
        results = run_parallel(prompt)
        return aggregate(results)
