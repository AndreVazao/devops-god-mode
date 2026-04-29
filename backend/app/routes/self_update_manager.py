from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.self_update_manager_service import self_update_manager_service

router = APIRouter(prefix="/api/self-update", tags=["self-update"])


class UpdatePlanRequest(BaseModel):
    current_version: str = "unknown"
    target_version: str = "latest"
    target_commit: str = "unknown"
    update_kind: str = "full_bundle"
    artifact_manifest: Optional[Dict[str, Any]] = None


class BackupRequest(BaseModel):
    plan_id: str
    backup_path: Optional[str] = None


class ApprovalRequest(BaseModel):
    plan_id: str
    approval_phrase: str = ""


class RunRecordRequest(BaseModel):
    plan_id: str
    status: str = "prepared"
    applied_version: Optional[str] = None
    smoke_test_result: Optional[Dict[str, Any]] = None


class RollbackRequest(BaseModel):
    plan_id: str
    rollback_phrase: str = ""


@router.get('/status')
async def status():
    return self_update_manager_service.get_status()


@router.post('/status')
async def post_status():
    return self_update_manager_service.get_status()


@router.get('/panel')
async def panel():
    return self_update_manager_service.panel()


@router.post('/panel')
async def post_panel():
    return self_update_manager_service.panel()


@router.get('/policy')
async def policy():
    return self_update_manager_service.policy()


@router.post('/policy')
async def post_policy():
    return self_update_manager_service.policy()


@router.post('/plan')
async def plan(payload: UpdatePlanRequest):
    return self_update_manager_service.create_plan(
        current_version=payload.current_version,
        target_version=payload.target_version,
        target_commit=payload.target_commit,
        update_kind=payload.update_kind,
        artifact_manifest=payload.artifact_manifest,
    )


@router.post('/backup')
async def backup(payload: BackupRequest):
    return self_update_manager_service.create_backup_record(
        plan_id=payload.plan_id,
        backup_path=payload.backup_path,
    )


@router.post('/approve')
async def approve(payload: ApprovalRequest):
    return self_update_manager_service.approve(
        plan_id=payload.plan_id,
        approval_phrase=payload.approval_phrase,
    )


@router.post('/record-run')
async def record_run(payload: RunRecordRequest):
    return self_update_manager_service.record_run(
        plan_id=payload.plan_id,
        status=payload.status,
        applied_version=payload.applied_version,
        smoke_test_result=payload.smoke_test_result,
    )


@router.post('/rollback')
async def rollback(payload: RollbackRequest):
    return self_update_manager_service.rollback_plan(
        plan_id=payload.plan_id,
        rollback_phrase=payload.rollback_phrase,
    )


@router.get('/latest')
async def latest():
    return self_update_manager_service.latest()


@router.post('/latest')
async def post_latest():
    return self_update_manager_service.latest()


@router.get('/package')
async def package():
    return self_update_manager_service.get_package()


@router.post('/package')
async def post_package():
    return self_update_manager_service.get_package()
