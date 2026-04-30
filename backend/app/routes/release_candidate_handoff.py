from fastapi import APIRouter
from pydantic import BaseModel

from app.services.release_candidate_handoff_service import release_candidate_handoff_service

router = APIRouter(prefix="/api/release-candidate-handoff", tags=["release-candidate-handoff"])


class HandoffRequest(BaseModel):
    version_label: str = "RC1"
    commit_sha: str = "b7f6174a7bd1c735534f9c4cdc9fce187402cb96"
    install_mode: str = "first_real_controlled_install"


@router.get('/status')
async def status():
    return release_candidate_handoff_service.get_status()


@router.post('/status')
async def post_status():
    return release_candidate_handoff_service.get_status()


@router.get('/panel')
async def panel():
    return release_candidate_handoff_service.panel()


@router.post('/panel')
async def post_panel():
    return release_candidate_handoff_service.panel()


@router.post('/build')
async def build(payload: HandoffRequest):
    return release_candidate_handoff_service.build_handoff(
        version_label=payload.version_label,
        commit_sha=payload.commit_sha,
        install_mode=payload.install_mode,
    )


@router.get('/latest')
async def latest():
    return release_candidate_handoff_service.latest()


@router.post('/latest')
async def post_latest():
    return release_candidate_handoff_service.latest()


@router.get('/package')
async def package():
    return release_candidate_handoff_service.get_package()


@router.post('/package')
async def post_package():
    return release_candidate_handoff_service.get_package()
