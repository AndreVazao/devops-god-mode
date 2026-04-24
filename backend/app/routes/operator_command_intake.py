from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_command_intake_service import operator_command_intake_service

router = APIRouter(prefix="/api/operator-command-intake", tags=["operator-command-intake"])


class OperatorCommandRequest(BaseModel):
    command_text: str
    tenant_id: str = "owner-andre"
    project_hint: str | None = None
    source_channel: str = "mobile_chat"


@router.get('/status')
async def status():
    return operator_command_intake_service.get_status()


@router.get('/package')
async def package():
    return operator_command_intake_service.get_package()


@router.post('/submit')
async def submit(payload: OperatorCommandRequest):
    return operator_command_intake_service.submit_command(
        command_text=payload.command_text,
        tenant_id=payload.tenant_id,
        project_hint=payload.project_hint,
        source_channel=payload.source_channel,
    )


@router.get('/commands')
async def commands(tenant_id: str = 'owner-andre', project_id: str | None = None, limit: int = 50):
    return operator_command_intake_service.list_commands(
        tenant_id=tenant_id,
        project_id=project_id,
        limit=limit,
    )


@router.get('/projects')
async def projects(tenant_id: str = 'owner-andre'):
    return operator_command_intake_service.list_project_memory(tenant_id=tenant_id)
