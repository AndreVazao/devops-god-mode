from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.pc_migration_control_center_service import pc_migration_control_center_service

router = APIRouter(prefix="/api/pc-migration-control", tags=["pc-migration-control"])


class PanelRequest(BaseModel):
    pc_profile: str = "auto"
    intent: str = "first_run_or_migration"


class AutoSetupRequest(BaseModel):
    pc_profile: str = "auto"
    include_backup: bool = True
    backup_destination_path: Optional[str] = None


@router.get('/status')
async def status():
    return pc_migration_control_center_service.get_status()


@router.post('/status')
async def post_status():
    return pc_migration_control_center_service.get_status()


@router.get('/panel')
async def panel(pc_profile: str = "auto", intent: str = "first_run_or_migration"):
    return pc_migration_control_center_service.panel(pc_profile=pc_profile, intent=intent)


@router.post('/panel')
async def post_panel(payload: PanelRequest):
    return pc_migration_control_center_service.panel(
        pc_profile=payload.pc_profile,
        intent=payload.intent,
    )


@router.post('/auto-setup')
async def auto_setup(payload: AutoSetupRequest):
    return pc_migration_control_center_service.auto_setup(
        pc_profile=payload.pc_profile,
        include_backup=payload.include_backup,
        backup_destination_path=payload.backup_destination_path,
    )


@router.get('/auto-mode')
async def auto_mode():
    return pc_migration_control_center_service.auto_mode_policy()


@router.post('/auto-mode')
async def post_auto_mode():
    return pc_migration_control_center_service.auto_mode_policy()


@router.get('/latest')
async def latest():
    return pc_migration_control_center_service.latest()


@router.post('/latest')
async def post_latest():
    return pc_migration_control_center_service.latest()


@router.get('/package')
async def package():
    return pc_migration_control_center_service.get_package()


@router.post('/package')
async def post_package():
    return pc_migration_control_center_service.get_package()
