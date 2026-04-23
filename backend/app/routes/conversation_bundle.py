from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.conversation_bundle_service import conversation_bundle_service

router = APIRouter(prefix="/api/conversation-bundles", tags=["conversation-bundles"])


class ConversationBundleCreateRequest(BaseModel):
    session_ids: list[str]
    project_hint: str | None = None
    bundle_name: str | None = None


class RepoPlanRequest(BaseModel):
    repository_name: str | None = None


@router.get('/status')
async def status():
    return conversation_bundle_service.get_status()


@router.get('/package')
async def package():
    return conversation_bundle_service.get_package()


@router.get('/list')
async def list_bundles():
    return conversation_bundle_service.list_bundles()


@router.get('/{bundle_id}')
async def get_bundle(bundle_id: str):
    bundle = conversation_bundle_service.get_bundle(bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail='bundle_not_found')
    return {"ok": True, "bundle": bundle}


@router.post('/create')
async def create_bundle(payload: ConversationBundleCreateRequest):
    return conversation_bundle_service.create_bundle_from_sessions(
        session_ids=payload.session_ids,
        project_hint=payload.project_hint,
        bundle_name=payload.bundle_name,
    )


@router.post('/auto-group')
async def auto_group():
    return conversation_bundle_service.auto_group_captured_sessions()


@router.post('/{bundle_id}/repo-plan')
async def build_repo_plan(bundle_id: str, payload: RepoPlanRequest):
    result = conversation_bundle_service.build_repo_materialization_plan(
        bundle_id=bundle_id,
        repository_name=payload.repository_name,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail='bundle_not_found')
    return result
