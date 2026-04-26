from fastapi import APIRouter
from pydantic import BaseModel

from app.services.self_update_service import self_update_service

router = APIRouter(prefix="/api/self-update", tags=["self-update"])


class UpdatePlanRequest(BaseModel):
    channel: str = "main"
    strategy: str = "git_pull_then_rebuild"


class UpdateRunRequest(BaseModel):
    channel: str = "main"
    dry_run: bool = True


@router.get('/status')
async def status():
    return self_update_service.get_status()


@router.get('/package')
async def package():
    return self_update_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return self_update_service.build_dashboard()


@router.get('/git-state')
async def git_state():
    return self_update_service.current_git_state()


@router.post('/plan')
async def plan(payload: UpdatePlanRequest):
    return self_update_service.create_update_plan(channel=payload.channel, strategy=payload.strategy)


@router.post('/backup-manifest')
async def backup_manifest():
    return self_update_service.create_backup_manifest()


@router.post('/execute')
async def execute(payload: UpdateRunRequest):
    return self_update_service.execute_safe_git_update(channel=payload.channel, dry_run=payload.dry_run)
