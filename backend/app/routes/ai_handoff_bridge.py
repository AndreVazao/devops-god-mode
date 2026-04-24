from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_handoff_bridge_service import ai_handoff_bridge_service

router = APIRouter(prefix="/api/ai-handoff", tags=["ai-handoff"])


class CreateLatestRequest(BaseModel):
    provider: str = "chatgpt"
    tenant_id: str = "owner-andre"


class CreateUnknownRequest(BaseModel):
    unknown: Dict[str, Any]
    provider: str = "chatgpt"
    tenant_id: str = "owner-andre"


class ResolveRequest(BaseModel):
    handoff_id: str
    provider_response: str
    learn_phrase: str = ""
    intent: str = "unknown"
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return ai_handoff_bridge_service.get_status()


@router.get('/package')
async def package():
    return ai_handoff_bridge_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return ai_handoff_bridge_service.build_dashboard()


@router.get('/handoffs')
async def list_handoffs(limit: int = 50, status: str | None = None):
    return ai_handoff_bridge_service.list_handoffs(limit=limit, status=status)


@router.get('/handoffs/{handoff_id}')
async def get_handoff(handoff_id: str):
    return ai_handoff_bridge_service.get_handoff(handoff_id)


@router.post('/from-latest-unknown')
async def from_latest_unknown(payload: CreateLatestRequest):
    return ai_handoff_bridge_service.create_handoff_from_latest_unknown(
        provider=payload.provider,
        tenant_id=payload.tenant_id,
    )


@router.post('/from-unknown')
async def from_unknown(payload: CreateUnknownRequest):
    return ai_handoff_bridge_service.create_handoff_from_unknown(
        unknown=payload.unknown,
        provider=payload.provider,
        tenant_id=payload.tenant_id,
    )


@router.post('/resolve')
async def resolve(payload: ResolveRequest):
    return ai_handoff_bridge_service.resolve_handoff(
        handoff_id=payload.handoff_id,
        provider_response=payload.provider_response,
        learn_phrase=payload.learn_phrase,
        intent=payload.intent,
        tenant_id=payload.tenant_id,
    )
