from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.download_install_center_v2_service import download_install_center_v2_service

router = APIRouter(prefix="/api/download-install-center-v2", tags=["download-install-center-v2"])


class PackageRequest(BaseModel):
    version: str = "latest"
    commit_sha: str = "unknown"
    github_run_url: Optional[str] = None
    artifact_base_url: Optional[str] = None


class ShareRequest(BaseModel):
    artifact_id: str = "android_apk"
    channel: str = "auto"
    filename: Optional[str] = None
    local_path: Optional[str] = None
    port: int = 8000


class TransferPlanRequest(BaseModel):
    direction: str = "phone_to_pc"
    file_label: str = "operator file"
    size_hint_mb: Optional[float] = None
    purpose: str = "use file in project"
    project_id: str = "GOD_MODE"


class IntakeRequest(BaseModel):
    project_id: str = "GOD_MODE"
    request_text: str = "usar ficheiro recebido no projeto"
    expected_file_type: str = "any"
    preferred_channel: str = "auto"


@router.get('/status')
async def status():
    return download_install_center_v2_service.get_status()


@router.post('/status')
async def post_status():
    return download_install_center_v2_service.get_status()


@router.get('/panel')
async def panel():
    return download_install_center_v2_service.panel()


@router.post('/panel')
async def post_panel():
    return download_install_center_v2_service.panel()


@router.get('/policy')
async def policy():
    return download_install_center_v2_service.policy()


@router.post('/policy')
async def post_policy():
    return download_install_center_v2_service.policy()


@router.post('/package')
async def package(payload: PackageRequest):
    return download_install_center_v2_service.build_package(
        version=payload.version,
        commit_sha=payload.commit_sha,
        github_run_url=payload.github_run_url,
        artifact_base_url=payload.artifact_base_url,
    )


@router.post('/share')
async def share(payload: ShareRequest):
    return download_install_center_v2_service.create_share(
        artifact_id=payload.artifact_id,
        channel=payload.channel,
        filename=payload.filename,
        local_path=payload.local_path,
        port=payload.port,
    )


@router.post('/transfer-plan')
async def transfer_plan(payload: TransferPlanRequest):
    return download_install_center_v2_service.transfer_plan(
        direction=payload.direction,
        file_label=payload.file_label,
        size_hint_mb=payload.size_hint_mb,
        purpose=payload.purpose,
        project_id=payload.project_id,
    )


@router.post('/intake-request')
async def intake_request(payload: IntakeRequest):
    return download_install_center_v2_service.intake_request(
        project_id=payload.project_id,
        request_text=payload.request_text,
        expected_file_type=payload.expected_file_type,
        preferred_channel=payload.preferred_channel,
    )


@router.get('/latest')
async def latest():
    return download_install_center_v2_service.latest()


@router.post('/latest')
async def post_latest():
    return download_install_center_v2_service.latest()


@router.get('/full-package')
async def full_package():
    return download_install_center_v2_service.get_package()


@router.post('/full-package')
async def post_full_package():
    return download_install_center_v2_service.get_package()
