class BaseAgent:
    name = "base"
    role = "generic"

    def run(self, task, context=None):
        """
        Executes the assigned task.
        :param task: The specific task description.
        :param context: Optional dictionary containing results from previous steps/agents.
        :return: Result of the execution.
        """
        raise NotImplementedError("Subclasses must implement the run method")
