from fastapi import APIRouter
from pydantic import BaseModel

from app.services.real_work_command_pipeline_service import real_work_command_pipeline_service

router = APIRouter(prefix="/api/real-work", tags=["real-work-command-pipeline"])


class RealWorkCommandRequest(BaseModel):
    command_text: str
    tenant_id: str = "owner-andre"
    requested_project: str | None = None
    auto_run: bool = True


@router.get('/status')
async def status():
    return real_work_command_pipeline_service.get_status()


@router.get('/package')
async def package():
    return real_work_command_pipeline_service.get_package()


@router.get('/latest')
async def latest():
    return real_work_command_pipeline_service.latest()


@router.post('/submit')
async def submit(payload: RealWorkCommandRequest):
    return real_work_command_pipeline_service.submit_command(
        command_text=payload.command_text,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
        auto_run=payload.auto_run,
    )
