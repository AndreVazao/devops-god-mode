from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_cleanup_optimizer_service import local_cleanup_optimizer_service

router = APIRouter(prefix="/api/local-cleanup", tags=["local-cleanup"])


class CleanupPlanRequest(BaseModel):
    keep_ollama_models: Optional[List[str]] = None
    broken_ollama_models: Optional[List[str]] = None
    allow_auto_ollama_remove: bool = True
    allow_windows_tuning_script: bool = True


class CleanupScriptRequest(BaseModel):
    plan_id: Optional[str] = None


class ApplySafeCleanupRequest(BaseModel):
    plan_id: Optional[str] = None
    approval_phrase: str = ""


@router.get('/status')
async def status():
    return local_cleanup_optimizer_service.get_status()


@router.post('/status')
async def post_status():
    return local_cleanup_optimizer_service.get_status()


@router.get('/panel')
async def panel():
    return local_cleanup_optimizer_service.panel()


@router.post('/panel')
async def post_panel():
    return local_cleanup_optimizer_service.panel()


@router.get('/policy')
async def policy():
    return local_cleanup_optimizer_service.policy()


@router.post('/policy')
async def post_policy():
    return local_cleanup_optimizer_service.policy()


@router.get('/scan')
async def scan():
    return local_cleanup_optimizer_service.scan()


@router.post('/scan')
async def post_scan():
    return local_cleanup_optimizer_service.scan()


@router.post('/plan')
async def plan(payload: CleanupPlanRequest):
    return local_cleanup_optimizer_service.plan(
        keep_ollama_models=payload.keep_ollama_models,
        broken_ollama_models=payload.broken_ollama_models,
        allow_auto_ollama_remove=payload.allow_auto_ollama_remove,
        allow_windows_tuning_script=payload.allow_windows_tuning_script,
    )


@router.post('/script')
async def script(payload: CleanupScriptRequest):
    return local_cleanup_optimizer_service.generate_script(plan_id=payload.plan_id)


@router.post('/apply-safe')
async def apply_safe(payload: ApplySafeCleanupRequest):
    return local_cleanup_optimizer_service.apply_safe_cleanup(
        plan_id=payload.plan_id,
        approval_phrase=payload.approval_phrase,
    )


@router.get('/latest')
async def latest():
    return local_cleanup_optimizer_service.latest()


@router.post('/latest')
async def post_latest():
    return local_cleanup_optimizer_service.latest()


@router.get('/package')
async def package():
    return local_cleanup_optimizer_service.get_package()


@router.post('/package')
async def post_package():
    return local_cleanup_optimizer_service.get_package()
