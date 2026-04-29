from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_ai_chat_reader_service import external_ai_chat_reader_service

router = APIRouter(prefix="/api/external-ai-chat-reader", tags=["external-ai-chat-reader"])


class ReaderPlanRequest(BaseModel):
    provider_id: str = "chatgpt"
    session_id: str | None = None
    conversation_url: str | None = None
    max_visible_messages: int = 30


class ScrollPlanRequest(BaseModel):
    provider_id: str = "chatgpt"
    session_id: str | None = None
    direction: str = "up"
    pages: int = 3


class SnapshotRequest(BaseModel):
    provider_id: str = "chatgpt"
    session_id: str | None = None
    raw_messages: List[Dict[str, Any]] = []


@router.get('/status')
async def status():
    return external_ai_chat_reader_service.get_status()


@router.post('/status')
async def post_status():
    return external_ai_chat_reader_service.get_status()


@router.get('/capability')
async def capability():
    return external_ai_chat_reader_service.capability_report()


@router.post('/capability')
async def post_capability():
    return external_ai_chat_reader_service.capability_report()


@router.get('/panel')
async def panel():
    return external_ai_chat_reader_service.build_panel()


@router.post('/panel')
async def post_panel():
    return external_ai_chat_reader_service.build_panel()


@router.get('/reader-plan')
async def reader_plan(provider_id: str = "chatgpt", session_id: str | None = None, conversation_url: str | None = None, max_visible_messages: int = 30):
    return external_ai_chat_reader_service.build_reader_plan(
        provider_id=provider_id,
        session_id=session_id,
        conversation_url=conversation_url,
        max_visible_messages=max_visible_messages,
    )


@router.post('/reader-plan')
async def post_reader_plan(payload: ReaderPlanRequest):
    return external_ai_chat_reader_service.build_reader_plan(
        provider_id=payload.provider_id,
        session_id=payload.session_id,
        conversation_url=payload.conversation_url,
        max_visible_messages=payload.max_visible_messages,
    )


@router.get('/scroll-plan')
async def scroll_plan(provider_id: str = "chatgpt", session_id: str | None = None, direction: str = "up", pages: int = 3):
    return external_ai_chat_reader_service.build_scroll_plan(
        provider_id=provider_id,
        session_id=session_id,
        direction=direction,
        pages=pages,
    )


@router.post('/scroll-plan')
async def post_scroll_plan(payload: ScrollPlanRequest):
    return external_ai_chat_reader_service.build_scroll_plan(
        provider_id=payload.provider_id,
        session_id=payload.session_id,
        direction=payload.direction,
        pages=payload.pages,
    )


@router.get('/runtime-instructions')
async def runtime_instructions(provider_id: str = "chatgpt"):
    return external_ai_chat_reader_service.runtime_instructions(provider_id=provider_id)


@router.post('/runtime-instructions')
async def post_runtime_instructions(provider_id: str = "chatgpt"):
    return external_ai_chat_reader_service.runtime_instructions(provider_id=provider_id)


@router.post('/normalize-snapshot')
async def normalize_snapshot(payload: SnapshotRequest):
    return external_ai_chat_reader_service.normalize_snapshot(
        provider_id=payload.provider_id,
        session_id=payload.session_id,
        raw_messages=payload.raw_messages,
    )


@router.get('/package')
async def package():
    return external_ai_chat_reader_service.get_package()


@router.post('/package')
async def post_package():
    return external_ai_chat_reader_service.get_package()
