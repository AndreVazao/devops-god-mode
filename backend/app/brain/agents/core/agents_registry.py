from app.brain.agents.dev.backend.python_agent import BackendPythonAgent
from app.brain.agents.dev.backend.node_agent import NodeAgent
from app.brain.agents.dev.frontend.html_agent import FrontendHTMLAgent
from app.brain.agents.dev.frontend.react_agent import ReactAgent
from app.brain.agents.dev.integration import IntegrationAgent
from app.brain.agents.devops.deploy import DeployAgent
from app.brain.agents.devops.cicd import CICDAgent
from app.brain.agents.qa.test import TestAgent
from app.brain.agents.security.security_agent import SecurityAgent
from app.brain.agents.ui_ux.ui_agent import UIAgent

AGENTS = {
    "python": BackendPythonAgent(),
    "node": NodeAgent(),
    "html": FrontendHTMLAgent(),
    "react": ReactAgent(),
    "integration": IntegrationAgent(),
    "deploy": DeployAgent(),
    "cicd": CICDAgent(),
    "test": TestAgent(),
    "security": SecurityAgent(),
    "ui_ux": UIAgent()
}
