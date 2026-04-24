from fastapi import APIRouter
from pydantic import BaseModel

from app.services.guided_mobile_command_center_service import guided_mobile_command_center_service

router = APIRouter(prefix="/api/guided-command-center", tags=["guided-command-center"])


class GuidedActionRequest(BaseModel):
    project: str = "GOD_MODE"
    action_id: str
    extra_instruction: str = ""
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return guided_mobile_command_center_service.get_status()


@router.get('/package')
async def package():
    return guided_mobile_command_center_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return guided_mobile_command_center_service.build_dashboard()


@router.get('/actions')
async def actions():
    return guided_mobile_command_center_service.list_actions()


@router.get('/projects/{project}/brief')
async def project_brief(project: str):
    return guided_mobile_command_center_service.build_project_brief(project)


@router.post('/prompt')
async def prompt(payload: GuidedActionRequest):
    return guided_mobile_command_center_service.build_prompt(
        project=payload.project,
        action_id=payload.action_id,
        extra_instruction=payload.extra_instruction,
    )


@router.post('/execute')
async def execute(payload: GuidedActionRequest):
    return guided_mobile_command_center_service.execute_guided_action(
        project=payload.project,
        action_id=payload.action_id,
        extra_instruction=payload.extra_instruction,
        tenant_id=payload.tenant_id,
    )
