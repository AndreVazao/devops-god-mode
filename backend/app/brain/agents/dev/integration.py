from app.brain.agents.core.base_agent import BaseAgent

class IntegrationAgent(BaseAgent):
    name = "Integration Agent"
    role = "integration"

    def run(self, task, context=None):
        # Simulation of integration logic
        return f"Integração feita com contexto: {context}"
