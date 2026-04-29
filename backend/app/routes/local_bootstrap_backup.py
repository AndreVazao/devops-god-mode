from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_bootstrap_backup_service import local_bootstrap_backup_service

router = APIRouter(prefix="/api/local-bootstrap-backup", tags=["local-bootstrap-backup"])


class BootstrapPlanRequest(BaseModel):
    pc_profile: str = "auto"


class InstallScriptRequest(BaseModel):
    pc_profile: str = "auto"
    destination_path: Optional[str] = None


class CreateBackupRequest(BaseModel):
    destination_path: Optional[str] = None
    include_data: bool = True


class RestorePreviewRequest(BaseModel):
    backup_path: str


@router.get('/status')
async def status():
    return local_bootstrap_backup_service.get_status()


@router.post('/status')
async def post_status():
    return local_bootstrap_backup_service.get_status()


@router.get('/panel')
async def panel():
    return local_bootstrap_backup_service.panel()


@router.post('/panel')
async def post_panel():
    return local_bootstrap_backup_service.panel()


@router.get('/requirements')
async def requirements():
    return local_bootstrap_backup_service.requirements()


@router.post('/requirements')
async def post_requirements():
    return local_bootstrap_backup_service.requirements()


@router.get('/plan')
async def plan(pc_profile: str = "auto"):
    return local_bootstrap_backup_service.bootstrap_plan(pc_profile=pc_profile)


@router.post('/plan')
async def post_plan(payload: BootstrapPlanRequest):
    return local_bootstrap_backup_service.bootstrap_plan(pc_profile=payload.pc_profile)


@router.post('/install-script')
async def install_script(payload: InstallScriptRequest):
    return local_bootstrap_backup_service.install_script(
        pc_profile=payload.pc_profile,
        destination_path=payload.destination_path,
    )


@router.post('/create-backup')
async def create_backup(payload: CreateBackupRequest):
    return local_bootstrap_backup_service.create_backup(
        destination_path=payload.destination_path,
        include_data=payload.include_data,
    )


@router.post('/restore-preview')
async def restore_preview(payload: RestorePreviewRequest):
    return local_bootstrap_backup_service.restore_preview(backup_path=payload.backup_path)


@router.get('/latest')
async def latest():
    return local_bootstrap_backup_service.latest()


@router.post('/latest')
async def post_latest():
    return local_bootstrap_backup_service.latest()


@router.get('/package')
async def package():
    return local_bootstrap_backup_service.get_package()


@router.post('/package')
async def post_package():
    return local_bootstrap_backup_service.get_package()
