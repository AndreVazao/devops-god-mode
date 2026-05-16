from app.brain.agents.core.base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    name = "Security Agent"
    role = "security"

    def run(self, task, context=None):
        return f"Security check completed for: {task}"
