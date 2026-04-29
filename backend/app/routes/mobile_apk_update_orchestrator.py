from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mobile_apk_update_orchestrator_service import mobile_apk_update_orchestrator_service

router = APIRouter(prefix="/api/mobile-apk-update", tags=["mobile-apk-update"])


class MobileUpdatePlanRequest(BaseModel):
    current_apk_version: str = "unknown"
    target_apk_version: str = "latest"
    package_id: str = "com.godmode.mobile"
    update_kind: str = "backend_only"
    apk_artifact_name: str = "GodModeMobile-debug.apk"
    apk_download_url: Optional[str] = None
    target_commit: str = "unknown"


class HandoffRequest(BaseModel):
    plan_id: str
    approval_phrase: str = ""


class AdbScriptRequest(BaseModel):
    plan_id: str
    local_apk_path: Optional[str] = None
    adb_approval_phrase: str = ""


class ResultRequest(BaseModel):
    plan_id: str
    status: str = "unknown"
    detail: str = ""
    apk_version_after: Optional[str] = None
    heartbeat_ok: bool = False


@router.get('/status')
async def status():
    return mobile_apk_update_orchestrator_service.get_status()


@router.post('/status')
async def post_status():
    return mobile_apk_update_orchestrator_service.get_status()


@router.get('/panel')
async def panel():
    return mobile_apk_update_orchestrator_service.panel()


@router.post('/panel')
async def post_panel():
    return mobile_apk_update_orchestrator_service.panel()


@router.get('/policy')
async def policy():
    return mobile_apk_update_orchestrator_service.policy()


@router.post('/policy')
async def post_policy():
    return mobile_apk_update_orchestrator_service.policy()


@router.post('/plan')
async def plan(payload: MobileUpdatePlanRequest):
    return mobile_apk_update_orchestrator_service.create_plan(
        current_apk_version=payload.current_apk_version,
        target_apk_version=payload.target_apk_version,
        package_id=payload.package_id,
        update_kind=payload.update_kind,
        apk_artifact_name=payload.apk_artifact_name,
        apk_download_url=payload.apk_download_url,
        target_commit=payload.target_commit,
    )


@router.post('/handoff')
async def handoff(payload: HandoffRequest):
    return mobile_apk_update_orchestrator_service.prepare_handoff(
        plan_id=payload.plan_id,
        approval_phrase=payload.approval_phrase,
    )


@router.post('/adb-script')
async def adb_script(payload: AdbScriptRequest):
    return mobile_apk_update_orchestrator_service.adb_script(
        plan_id=payload.plan_id,
        local_apk_path=payload.local_apk_path,
        adb_approval_phrase=payload.adb_approval_phrase,
    )


@router.post('/record-result')
async def record_result(payload: ResultRequest):
    return mobile_apk_update_orchestrator_service.record_result(
        plan_id=payload.plan_id,
        status=payload.status,
        detail=payload.detail,
        apk_version_after=payload.apk_version_after,
        heartbeat_ok=payload.heartbeat_ok,
    )


@router.get('/latest')
async def latest():
    return mobile_apk_update_orchestrator_service.latest()


@router.post('/latest')
async def post_latest():
    return mobile_apk_update_orchestrator_service.latest()


@router.get('/package')
async def package():
    return mobile_apk_update_orchestrator_service.get_package()


@router.post('/package')
async def post_package():
    return mobile_apk_update_orchestrator_service.get_package()
