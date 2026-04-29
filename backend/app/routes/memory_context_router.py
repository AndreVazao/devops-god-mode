from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.memory_context_router_service import memory_context_router_service

router = APIRouter(prefix="/api/memory-context-router", tags=["memory-context-router"])


class PrepareProjectContextRequest(BaseModel):
    project_id: str
    source: str = "existing_or_new_project"
    idea: Optional[str] = None
    max_chars: int = 8000


class HandoffPlanRequest(BaseModel):
    project_id: str
    from_provider: str = "chatgpt"
    reason: str = "limit_or_capacity"


@router.get('/status')
async def status():
    return memory_context_router_service.get_status()


@router.post('/status')
async def post_status():
    return memory_context_router_service.get_status()


@router.get('/panel')
async def panel():
    return memory_context_router_service.panel()


@router.post('/panel')
async def post_panel():
    return memory_context_router_service.panel()


@router.get('/provider-policy')
async def provider_policy():
    return memory_context_router_service.provider_policy()


@router.post('/provider-policy')
async def post_provider_policy():
    return memory_context_router_service.provider_policy()


@router.get('/obsidian-policy')
async def obsidian_policy():
    return memory_context_router_service.obsidian_policy()


@router.post('/obsidian-policy')
async def post_obsidian_policy():
    return memory_context_router_service.obsidian_policy()


@router.post('/prepare-project')
async def prepare_project(payload: PrepareProjectContextRequest):
    return memory_context_router_service.prepare_project_context(
        project_id=payload.project_id,
        source=payload.source,
        idea=payload.idea,
        max_chars=payload.max_chars,
    )


@router.post('/prepare-latest-new-project')
async def prepare_latest_new_project():
    return memory_context_router_service.prepare_latest_new_project()


@router.post('/prepare-priority-projects')
async def prepare_priority_projects(limit: int = 12):
    return memory_context_router_service.prepare_priority_projects(limit=limit)


@router.post('/handoff-plan')
async def handoff_plan(payload: HandoffPlanRequest):
    return memory_context_router_service.handoff_plan(
        project_id=payload.project_id,
        from_provider=payload.from_provider,
        reason=payload.reason,
    )


@router.get('/latest')
async def latest():
    return memory_context_router_service.latest()


@router.post('/latest')
async def post_latest():
    return memory_context_router_service.latest()


@router.get('/package')
async def package():
    return memory_context_router_service.get_package()


@router.post('/package')
async def post_package():
    return memory_context_router_service.get_package()
