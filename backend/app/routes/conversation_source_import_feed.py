from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation_source_import_feed_service import conversation_source_import_feed_service

router = APIRouter(prefix="/api/conversation-source-import-feed", tags=["conversation-source-import-feed"])


class ImportTextRequest(BaseModel):
    transcript_text: str
    provider: str = "manual_paste"
    project_hint: str = "GOD_MODE"
    title: str = "Imported conversation"
    source_ref: str | None = None
    tenant_id: str = "owner-andre"
    create_review_card: bool = True


class ImportMessagesRequest(BaseModel):
    messages: list[dict[str, Any]]
    provider: str = "manual_messages"
    project_hint: str = "GOD_MODE"
    title: str = "Imported message list"
    source_ref: str | None = None
    tenant_id: str = "owner-andre"


class ReviewCardsRequest(BaseModel):
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return conversation_source_import_feed_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return conversation_source_import_feed_service.policy()


@router.post("/import-text")
def import_text(payload: ImportTextRequest) -> dict[str, Any]:
    return conversation_source_import_feed_service.import_text(
        transcript_text=payload.transcript_text,
        provider=payload.provider,
        project_hint=payload.project_hint,
        title=payload.title,
        source_ref=payload.source_ref,
        tenant_id=payload.tenant_id,
        create_review_card=payload.create_review_card,
    )


@router.post("/import-messages")
def import_messages(payload: ImportMessagesRequest) -> dict[str, Any]:
    return conversation_source_import_feed_service.import_messages(
        messages=payload.messages,
        provider=payload.provider,
        project_hint=payload.project_hint,
        title=payload.title,
        source_ref=payload.source_ref,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-review-cards")
def create_review_cards(payload: ReviewCardsRequest) -> dict[str, Any]:
    return conversation_source_import_feed_service.create_review_cards(tenant_id=payload.tenant_id)


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return conversation_source_import_feed_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return conversation_source_import_feed_service.package()
