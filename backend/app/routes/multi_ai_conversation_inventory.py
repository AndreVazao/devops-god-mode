from fastapi import APIRouter
from pydantic import BaseModel

from app.services.multi_ai_conversation_inventory_service import multi_ai_conversation_inventory_service

router = APIRouter(prefix="/api/multi-ai-conversation-inventory", tags=["multi-ai-conversation-inventory"])


class StageConversationRequest(BaseModel):
    provider: str
    title: str
    snippet: str = ""
    conversation_url: str | None = None
    project_hint: str | None = None
    tenant_id: str = "owner-andre"
    source_status: str = "manual_seed"


class SeedFromCommandRequest(BaseModel):
    command_id: str | None = None
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return multi_ai_conversation_inventory_service.get_status()


@router.get('/package')
async def package():
    return multi_ai_conversation_inventory_service.get_package()


@router.post('/stage')
async def stage(payload: StageConversationRequest):
    return multi_ai_conversation_inventory_service.stage_conversation(
        provider=payload.provider,
        title=payload.title,
        snippet=payload.snippet,
        conversation_url=payload.conversation_url,
        project_hint=payload.project_hint,
        tenant_id=payload.tenant_id,
        source_status=payload.source_status,
    )


@router.post('/seed-from-command')
async def seed_from_command(payload: SeedFromCommandRequest):
    return multi_ai_conversation_inventory_service.seed_from_operator_command(
        command_id=payload.command_id,
        tenant_id=payload.tenant_id,
    )


@router.get('/conversations')
async def conversations(
    tenant_id: str = 'owner-andre',
    project_id: str | None = None,
    provider: str | None = None,
    limit: int = 100,
):
    return multi_ai_conversation_inventory_service.list_conversations(
        tenant_id=tenant_id,
        project_id=project_id,
        provider=provider,
        limit=limit,
    )


@router.get('/project-map')
async def project_map(tenant_id: str = 'owner-andre'):
    return multi_ai_conversation_inventory_service.build_project_map(tenant_id=tenant_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return multi_ai_conversation_inventory_service.build_inventory_dashboard(tenant_id=tenant_id)
