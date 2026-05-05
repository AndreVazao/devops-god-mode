from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation_requirement_ledger_service import conversation_requirement_ledger_service

router = APIRouter(prefix="/api/conversation-requirement-ledger", tags=["conversation-requirement-ledger"])


class AnalyzeTextRequest(BaseModel):
    project_key: str = "GOD_MODE"
    transcript_text: str
    source_provider: str = "unknown"
    source_id: str | None = None
    store: bool = True


class AnalyzeMessagesRequest(BaseModel):
    project_key: str = "GOD_MODE"
    messages: list[dict[str, Any]]
    source_provider: str = "unknown"
    source_id: str | None = None
    store: bool = True


class ProjectRequest(BaseModel):
    project_key: str = "GOD_MODE"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return conversation_requirement_ledger_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return conversation_requirement_ledger_service.policy()


@router.post("/analyze-text")
def analyze_text(payload: AnalyzeTextRequest) -> dict[str, Any]:
    return conversation_requirement_ledger_service.analyze_text(
        project_key=payload.project_key,
        transcript_text=payload.transcript_text,
        source_provider=payload.source_provider,
        source_id=payload.source_id,
        store=payload.store,
    )


@router.post("/analyze-messages")
def analyze_messages(payload: AnalyzeMessagesRequest) -> dict[str, Any]:
    return conversation_requirement_ledger_service.analyze_messages(
        project_key=payload.project_key,
        messages=payload.messages,
        source_provider=payload.source_provider,
        source_id=payload.source_id,
        store=payload.store,
    )


@router.post("/compare-project")
def compare_project(payload: ProjectRequest) -> dict[str, Any]:
    return conversation_requirement_ledger_service.compare_project(payload.project_key)


@router.get("/open-requirements")
@router.post("/open-requirements")
def open_requirements(project_key: str | None = None) -> dict[str, Any]:
    return conversation_requirement_ledger_service.list_open_requirements(project_key=project_key)


@router.post("/realness-scorecard")
def realness_scorecard(payload: ProjectRequest) -> dict[str, Any]:
    return conversation_requirement_ledger_service.realness_scorecard(payload.project_key)


@router.get("/package")
@router.post("/package")
def package(project_key: str = "GOD_MODE") -> dict[str, Any]:
    return conversation_requirement_ledger_service.package(project_key=project_key)
