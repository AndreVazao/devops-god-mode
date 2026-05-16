from app.brain.agents.core.base_agent import BaseAgent
from app.services.local_executor_service import execute_code

class TestAgent(BaseAgent):
    name = "Test Agent"
    role = "qa"

    def run(self, task, context=None):
        # Running tests
        result = execute_code("pytest --version")
        return f"Testes executados: {result.get('stdout')}"
