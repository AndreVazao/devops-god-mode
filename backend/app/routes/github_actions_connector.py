from fastapi import APIRouter
from pydantic import BaseModel

from app.services.github_actions_connector_service import github_actions_connector_service

router = APIRouter(prefix="/api/github-actions-connector", tags=["github-actions-connector"])


class GitHubActionsConnectorRequest(BaseModel):
    repository_full_name: str
    target_project: str
    environment_name: str
    workflow_file_path: str
    branch_name: str = "main"


@router.get('/status')
async def status():
    return github_actions_connector_service.get_status()


@router.get('/package')
async def package():
    return github_actions_connector_service.get_package()


@router.post('/build')
async def build(payload: GitHubActionsConnectorRequest):
    return github_actions_connector_service.build_connector_plan(
        repository_full_name=payload.repository_full_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
        workflow_file_path=payload.workflow_file_path,
        branch_name=payload.branch_name,
    )
