from app.brain.agents.core.base_agent import BaseAgent

class UIAgent(BaseAgent):
    name = "UI Agent"
    role = "ui_ux"

    def run(self, task, context=None):
        return f"UI/UX Design proposed for: {task}"
