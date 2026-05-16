from app.brain.agents.core.base_agent import BaseAgent
from app.services.local_executor_service import execute_code

class DeployAgent(BaseAgent):
    name = "Deploy Agent"
    role = "devops"

    def run(self, task, context=None):
        # Simulation of deploy command
        result = execute_code("echo 'Deploying to Vercel...' && vercel --version")
        return f"Deploy executado: {result.get('stdout')}"
