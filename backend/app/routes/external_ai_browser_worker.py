from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_ai_browser_worker_service import external_ai_browser_worker_service

router = APIRouter(prefix="/api/external-ai-browser", tags=["external-ai-browser"])


class ExternalAiBrowserPrepareRequest(BaseModel):
    provider_id: str = "chatgpt"
    conversation_url: str | None = None
    operator_goal: str | None = None
    tenant_id: str = "owner-andre"
    open_browser: bool = False


class ExternalAiBrowserProbeRequest(BaseModel):
    provider_id: str = "chatgpt"
    conversation_url: str | None = None
    session_id: str | None = None


class ExternalAiLoginConfirmRequest(BaseModel):
    session_id: str
    provider_id: str = "chatgpt"
    operator_confirmed: bool = True


@router.get('/status')
async def status():
    return external_ai_browser_worker_service.get_status()


@router.post('/status')
async def post_status():
    return external_ai_browser_worker_service.get_status()


@router.get('/capability')
async def capability():
    return external_ai_browser_worker_service.capability_report()


@router.post('/capability')
async def post_capability():
    return external_ai_browser_worker_service.capability_report()


@router.get('/panel')
async def panel():
    return external_ai_browser_worker_service.build_panel()


@router.post('/panel')
async def post_panel():
    return external_ai_browser_worker_service.build_panel()


@router.post('/prepare')
async def prepare(payload: ExternalAiBrowserPrepareRequest):
    return external_ai_browser_worker_service.prepare_session(
        provider_id=payload.provider_id,
        conversation_url=payload.conversation_url,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
        open_browser=payload.open_browser,
    )


@router.get('/probe')
async def probe(provider_id: str = "chatgpt", conversation_url: str | None = None, session_id: str | None = None):
    return external_ai_browser_worker_service.open_session_probe(
        provider_id=provider_id,
        conversation_url=conversation_url,
        session_id=session_id,
    )


@router.post('/probe')
async def post_probe(payload: ExternalAiBrowserProbeRequest):
    return external_ai_browser_worker_service.open_session_probe(
        provider_id=payload.provider_id,
        conversation_url=payload.conversation_url,
        session_id=payload.session_id,
    )


@router.post('/confirm-login')
async def confirm_login(payload: ExternalAiLoginConfirmRequest):
    return external_ai_browser_worker_service.confirm_manual_login(
        session_id=payload.session_id,
        provider_id=payload.provider_id,
        operator_confirmed=payload.operator_confirmed,
    )


@router.get('/package')
async def package():
    return external_ai_browser_worker_service.get_package()


@router.post('/package')
async def post_package():
    return external_ai_browser_worker_service.get_package()
