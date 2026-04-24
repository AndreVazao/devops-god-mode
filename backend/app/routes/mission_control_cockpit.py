from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mission_control_cockpit_service import mission_control_cockpit_service

router = APIRouter(prefix="/api/mission-control", tags=["mission-control"])


class CommandRequest(BaseModel):
    command_text: str
    project_hint: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return mission_control_cockpit_service.get_status()


@router.get('/package')
async def package():
    return mission_control_cockpit_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return mission_control_cockpit_service.build_dashboard(tenant_id=tenant_id)


@router.post('/command')
async def command(payload: CommandRequest):
    return mission_control_cockpit_service.submit_mobile_command(
        command_text=payload.command_text,
        project_hint=payload.project_hint,
        tenant_id=payload.tenant_id,
    )
