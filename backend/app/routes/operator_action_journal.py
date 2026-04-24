from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_action_journal_service import operator_action_journal_service

router = APIRouter(prefix="/api/operator-action-journal", tags=["operator-action-journal"])


class OperatorActionJournalLogRequest(BaseModel):
    tenant_id: str
    thread_id: str
    event_type: str
    summary: str
    outcome: str = "recorded"
    details: dict | None = None
    origin: str = "operator_chat_sync_frontend"


@router.get('/status')
async def status():
    return operator_action_journal_service.get_status()


@router.get('/package')
async def package():
    return operator_action_journal_service.get_package()


@router.get('/list')
async def list_entries(tenant_id: str | None = None, thread_id: str | None = None, limit: int = 50):
    return operator_action_journal_service.list_entries(tenant_id=tenant_id, thread_id=thread_id, limit=limit)


@router.post('/log')
async def log(payload: OperatorActionJournalLogRequest):
    return operator_action_journal_service.log_event(
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        event_type=payload.event_type,
        summary=payload.summary,
        outcome=payload.outcome,
        details=payload.details,
        origin=payload.origin,
    )
