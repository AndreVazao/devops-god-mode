from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_chat_cleanup_archive_service import external_chat_cleanup_archive_service

router = APIRouter(prefix="/api/external-chat-cleanup", tags=["external-chat-cleanup"])


class InventoryRequest(BaseModel):
    provider_id: str = "chatgpt"
    project_id: Optional[str] = None
    conversations: Optional[List[Dict[str, Any]]] = None


class ExtractMemoryRequest(BaseModel):
    conversation: Dict[str, Any]
    project_id: Optional[str] = None
    extraction_summary: str = ""
    backlog_items: Optional[List[str]] = None
    decisions: Optional[List[str]] = None


class CleanupPlanRequest(BaseModel):
    provider_id: str = "chatgpt"
    project_id: Optional[str] = None
    project_done: bool = False
    conversations: Optional[List[Dict[str, Any]]] = None


class ApproveCleanupRequest(BaseModel):
    cleanup_plan_id: str
    approval_phrase: str = ""


@router.get('/status')
async def status():
    return external_chat_cleanup_archive_service.get_status()


@router.post('/status')
async def post_status():
    return external_chat_cleanup_archive_service.get_status()


@router.get('/panel')
async def panel():
    return external_chat_cleanup_archive_service.panel()


@router.post('/panel')
async def post_panel():
    return external_chat_cleanup_archive_service.panel()


@router.get('/policy')
async def policy():
    return external_chat_cleanup_archive_service.policy()


@router.post('/policy')
async def post_policy():
    return external_chat_cleanup_archive_service.policy()


@router.post('/inventory')
async def inventory(payload: InventoryRequest):
    return external_chat_cleanup_archive_service.inventory(
        provider_id=payload.provider_id,
        conversations=payload.conversations,
        project_id=payload.project_id,
    )


@router.post('/extract-memory')
async def extract_memory(payload: ExtractMemoryRequest):
    return external_chat_cleanup_archive_service.extract_memory(
        conversation=payload.conversation,
        project_id=payload.project_id,
        extraction_summary=payload.extraction_summary,
        backlog_items=payload.backlog_items,
        decisions=payload.decisions,
    )


@router.post('/plan')
async def cleanup_plan(payload: CleanupPlanRequest):
    return external_chat_cleanup_archive_service.cleanup_plan(
        provider_id=payload.provider_id,
        project_id=payload.project_id,
        project_done=payload.project_done,
        conversations=payload.conversations,
    )


@router.post('/approve-plan')
async def approve_plan(payload: ApproveCleanupRequest):
    return external_chat_cleanup_archive_service.approve_cleanup_plan(
        cleanup_plan_id=payload.cleanup_plan_id,
        approval_phrase=payload.approval_phrase,
    )


@router.get('/latest')
async def latest():
    return external_chat_cleanup_archive_service.latest()


@router.post('/latest')
async def post_latest():
    return external_chat_cleanup_archive_service.latest()


@router.get('/package')
async def package():
    return external_chat_cleanup_archive_service.get_package()


@router.post('/package')
async def post_package():
    return external_chat_cleanup_archive_service.get_package()
