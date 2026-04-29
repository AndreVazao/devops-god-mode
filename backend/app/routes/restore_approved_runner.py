from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.restore_approved_runner_service import restore_approved_runner_service

router = APIRouter(prefix="/api/restore-approved", tags=["restore-approved"])


class RestorePreviewRequest(BaseModel):
    backup_path: str
    restore_filter: Optional[List[str]] = None


class RestoreRunRequest(BaseModel):
    backup_path: str
    approval_phrase: str
    restore_filter: Optional[List[str]] = None
    overwrite: bool = False


class RollbackRequest(BaseModel):
    pre_restore_backup_path: str
    approval_phrase: str


@router.get('/status')
async def status():
    return restore_approved_runner_service.get_status()


@router.post('/status')
async def post_status():
    return restore_approved_runner_service.get_status()


@router.get('/panel')
async def panel():
    return restore_approved_runner_service.panel()


@router.post('/panel')
async def post_panel():
    return restore_approved_runner_service.panel()


@router.post('/preview')
async def preview(payload: RestorePreviewRequest):
    return restore_approved_runner_service.preview(
        backup_path=payload.backup_path,
        restore_filter=payload.restore_filter,
    )


@router.post('/run')
async def run(payload: RestoreRunRequest):
    return restore_approved_runner_service.restore(
        backup_path=payload.backup_path,
        approval_phrase=payload.approval_phrase,
        restore_filter=payload.restore_filter,
        overwrite=payload.overwrite,
    )


@router.post('/rollback')
async def rollback(payload: RollbackRequest):
    return restore_approved_runner_service.rollback(
        pre_restore_backup_path=payload.pre_restore_backup_path,
        approval_phrase=payload.approval_phrase,
    )


@router.get('/latest')
async def latest():
    return restore_approved_runner_service.latest()


@router.post('/latest')
async def post_latest():
    return restore_approved_runner_service.latest()


@router.get('/package')
async def package():
    return restore_approved_runner_service.get_package()


@router.post('/package')
async def post_package():
    return restore_approved_runner_service.get_package()
