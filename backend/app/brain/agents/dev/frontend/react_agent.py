from app.brain.agents.core.base_agent import BaseAgent
class ReactAgent(BaseAgent):
    name = "React Agent"
    role = "frontend"
    def run(self, task, context=None):
        return f"React components for: {task}"
