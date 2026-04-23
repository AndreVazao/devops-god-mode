from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_resumable_action_service import operator_resumable_action_service

router = APIRouter(prefix="/api/operator-resumable-action", tags=["operator-resumable-action"])


class OperatorResumableActionCreateRequest(BaseModel):
    tenant_id: str
    thread_id: str
    provider_name: str
    action_kind: str
    purpose_summary: str
    resume_strategy: str = "retry_from_latest_safe_checkpoint"
    requires_fresh_provider_session: bool = False


class OperatorResumableActionSyncRequest(BaseModel):
    action_id: str
    payload_summary: str


class OperatorResumableActionResumeRequest(BaseModel):
    action_id: str
    provider_session_still_valid: bool


@router.get('/status')
async def status():
    return operator_resumable_action_service.get_status()


@router.get('/package')
async def package():
    return operator_resumable_action_service.get_package()


@router.get('/list')
async def list_actions(tenant_id: str | None = None, thread_id: str | None = None):
    return operator_resumable_action_service.list_actions(tenant_id=tenant_id, thread_id=thread_id)


@router.post('/create')
async def create(payload: OperatorResumableActionCreateRequest):
    return operator_resumable_action_service.create_action(
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        provider_name=payload.provider_name,
        action_kind=payload.action_kind,
        purpose_summary=payload.purpose_summary,
        resume_strategy=payload.resume_strategy,
        requires_fresh_provider_session=payload.requires_fresh_provider_session,
    )


@router.post('/submit-offline-sync')
async def submit_offline_sync(payload: OperatorResumableActionSyncRequest):
    return operator_resumable_action_service.submit_offline_sync(
        action_id=payload.action_id,
        payload_summary=payload.payload_summary,
    )


@router.post('/resume')
async def resume(payload: OperatorResumableActionResumeRequest):
    return operator_resumable_action_service.resume_action(
        action_id=payload.action_id,
        provider_session_still_valid=payload.provider_session_still_valid,
    )
