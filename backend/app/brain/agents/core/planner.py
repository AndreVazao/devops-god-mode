def create_agent_plan(task):
    steps = []
    task_lower = task.lower()

    if "app" in task_lower or "web" in task_lower or "projeto" in task_lower:
        steps = [
            {"agent": "ui_ux", "task": f"Projetar interface para: {task}"},
            {"agent": "python", "task": "Desenvolver API backend"},
            {"agent": "react", "task": "Desenvolver interface frontend em React"},
            {"agent": "integration", "task": "Integrar frontend e backend"},
            {"agent": "security", "task": "Realizar auditoria de segurança"},
            {"agent": "test", "task": "Executar suite de testes"},
            {"agent": "cicd", "task": "Configurar Pipeline CI/CD"},
            {"agent": "deploy", "task": "Realizar deploy em produção"},
        ]
    else:
        steps = [
            {"agent": "python", "task": task},
            {"agent": "test", "task": "Verificar execução"}
        ]

    return steps
