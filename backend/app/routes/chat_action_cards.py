from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_action_cards_service import chat_action_cards_service

router = APIRouter(prefix="/api/chat-action-cards", tags=["chat-action-cards"])


class CreateCardRequest(BaseModel):
    thread_id: str
    title: str
    body: str = ""
    actions: list[dict]
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"
    source: str = "chat"
    priority: str = "medium"


class HomeChatCardsRequest(BaseModel):
    message: str
    thread_id: str | None = None
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"


class ExecuteCardRequest(BaseModel):
    card_id: str
    action_id: str
    tenant_id: str = "owner-andre"


class DismissCardRequest(BaseModel):
    card_id: str
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return chat_action_cards_service.get_status()


@router.get('/package')
async def package():
    return chat_action_cards_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return chat_action_cards_service.build_dashboard(tenant_id=tenant_id)


@router.get('/cards')
async def cards(tenant_id: str = "owner-andre", thread_id: str | None = None, status: str | None = None, limit: int = 100):
    return chat_action_cards_service.list_cards(tenant_id=tenant_id, thread_id=thread_id, status=status, limit=limit)


@router.post('/create')
async def create(payload: CreateCardRequest):
    return chat_action_cards_service.create_card(
        thread_id=payload.thread_id,
        title=payload.title,
        body=payload.body,
        actions=payload.actions,
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
        source=payload.source,
        priority=payload.priority,
    )


@router.post('/from-home-chat')
async def from_home_chat(payload: HomeChatCardsRequest):
    return chat_action_cards_service.create_cards_from_home_chat(
        message=payload.message,
        thread_id=payload.thread_id,
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
    )


@router.post('/execute')
async def execute(payload: ExecuteCardRequest):
    return chat_action_cards_service.execute_card_action(
        card_id=payload.card_id,
        action_id=payload.action_id,
        tenant_id=payload.tenant_id,
    )


@router.post('/dismiss')
async def dismiss(payload: DismissCardRequest):
    return chat_action_cards_service.dismiss_card(card_id=payload.card_id, tenant_id=payload.tenant_id)
