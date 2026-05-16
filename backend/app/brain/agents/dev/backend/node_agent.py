from app.brain.agents.core.base_agent import BaseAgent
class NodeAgent(BaseAgent):
    name = "Node Agent"
    role = "backend"
    def run(self, task, context=None):
        return f"Node.js logic for: {task}"
