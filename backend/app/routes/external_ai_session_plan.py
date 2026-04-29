from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_ai_session_plan_service import external_ai_session_plan_service

router = APIRouter(prefix="/api/external-ai-session", tags=["external-ai-session"])


class ExternalAiPlanRequest(BaseModel):
    provider_id: str = "chatgpt"
    conversation_url: str | None = None
    operator_goal: str | None = None
    tenant_id: str = "owner-andre"


class ExternalAiLoginPopupRequest(BaseModel):
    provider_id: str = "chatgpt"
    session_id: str | None = None
    reason: str = "login_required"


class ExternalAiCheckpointRequest(BaseModel):
    session_id: str
    step: str
    status: str = "checkpoint_saved"
    safe_state: Dict[str, Any] | None = None


class ExternalAiResumeRequest(BaseModel):
    session_id: str | None = None


@router.get('/status')
async def status():
    return external_ai_session_plan_service.get_status()


@router.post('/status')
async def post_status():
    return external_ai_session_plan_service.get_status()


@router.get('/providers')
async def providers():
    return external_ai_session_plan_service.providers()


@router.post('/providers')
async def post_providers():
    return external_ai_session_plan_service.providers()


@router.get('/policy')
async def policy():
    return external_ai_session_plan_service.security_policy()


@router.post('/policy')
async def post_policy():
    return external_ai_session_plan_service.security_policy()


@router.get('/resume-contract')
async def resume_contract():
    return external_ai_session_plan_service.resume_contract()


@router.post('/resume-contract')
async def post_resume_contract():
    return external_ai_session_plan_service.resume_contract()


@router.post('/plan')
async def plan(payload: ExternalAiPlanRequest):
    return external_ai_session_plan_service.create_plan(
        provider_id=payload.provider_id,
        conversation_url=payload.conversation_url,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.post('/login-popup')
async def login_popup(payload: ExternalAiLoginPopupRequest):
    return external_ai_session_plan_service.request_login_popup(
        provider_id=payload.provider_id,
        session_id=payload.session_id,
        reason=payload.reason,
    )


@router.post('/checkpoint')
async def checkpoint(payload: ExternalAiCheckpointRequest):
    return external_ai_session_plan_service.record_checkpoint(
        session_id=payload.session_id,
        step=payload.step,
        status=payload.status,
        safe_state=payload.safe_state,
    )


@router.get('/resume')
async def resume(session_id: str | None = None):
    return external_ai_session_plan_service.resume_plan(session_id=session_id)


@router.post('/resume')
async def post_resume(payload: ExternalAiResumeRequest):
    return external_ai_session_plan_service.resume_plan(session_id=payload.session_id)


@router.get('/latest')
async def latest():
    return external_ai_session_plan_service.latest()


@router.post('/latest')
async def post_latest():
    return external_ai_session_plan_service.latest()


@router.get('/package')
async def package():
    return external_ai_session_plan_service.get_package()


@router.post('/package')
async def post_package():
    return external_ai_session_plan_service.get_package()
