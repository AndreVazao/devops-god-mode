from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repo_file_patch_hub_service import repo_file_patch_hub_service

router = APIRouter(prefix="/api/repo-file-patch", tags=["repo-file-patch"])


class PatchPlanRequest(BaseModel):
    project_id: str = "GOD_MODE"
    goal: str = "apply safe repo/file patch"
    target_repo: str = "AndreVazao/devops-god-mode"
    base_branch: str = "main"
    target_branch: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    validation_commands: Optional[List[str]] = None


class PlanIdRequest(BaseModel):
    plan_id: str


class ApprovalRequest(BaseModel):
    plan_id: str
    approval_phrase: str = ""


class RunRecordRequest(BaseModel):
    plan_id: str
    status: str = "completed"
    pr_url: Optional[str] = None
    validation_result: Optional[Dict[str, Any]] = None
    rollback_available: bool = True


@router.get('/status')
async def status():
    return repo_file_patch_hub_service.get_status()


@router.post('/status')
async def post_status():
    return repo_file_patch_hub_service.get_status()


@router.get('/panel')
async def panel():
    return repo_file_patch_hub_service.panel()


@router.post('/panel')
async def post_panel():
    return repo_file_patch_hub_service.panel()


@router.get('/policy')
async def policy():
    return repo_file_patch_hub_service.policy()


@router.post('/policy')
async def post_policy():
    return repo_file_patch_hub_service.policy()


@router.post('/plan')
async def plan(payload: PatchPlanRequest):
    return repo_file_patch_hub_service.create_plan(
        project_id=payload.project_id,
        goal=payload.goal,
        target_repo=payload.target_repo,
        base_branch=payload.base_branch,
        target_branch=payload.target_branch,
        files=payload.files,
        validation_commands=payload.validation_commands,
    )


@router.post('/preview')
async def preview(payload: PlanIdRequest):
    return repo_file_patch_hub_service.preview(plan_id=payload.plan_id)


@router.post('/checkpoint')
async def checkpoint(payload: PlanIdRequest):
    return repo_file_patch_hub_service.checkpoint(plan_id=payload.plan_id)


@router.post('/approve')
async def approve(payload: ApprovalRequest):
    return repo_file_patch_hub_service.approve(
        plan_id=payload.plan_id,
        approval_phrase=payload.approval_phrase,
    )


@router.post('/record-run')
async def record_run(payload: RunRecordRequest):
    return repo_file_patch_hub_service.record_run(
        plan_id=payload.plan_id,
        status=payload.status,
        pr_url=payload.pr_url,
        validation_result=payload.validation_result,
        rollback_available=payload.rollback_available,
    )


@router.get('/latest')
async def latest():
    return repo_file_patch_hub_service.latest()


@router.post('/latest')
async def post_latest():
    return repo_file_patch_hub_service.latest()


@router.get('/package')
async def package():
    return repo_file_patch_hub_service.get_package()


@router.post('/package')
async def post_package():
    return repo_file_patch_hub_service.get_package()
