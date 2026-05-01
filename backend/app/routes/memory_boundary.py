from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.memory_boundary_service import memory_boundary_service


router = APIRouter(prefix="/api/memory-boundary", tags=["memory-boundary"])


class ClassifyNoteRequest(BaseModel):
    title: str
    body: str | None = None


class AiHandoffTemplateRequest(BaseModel):
    project: str
    repo: str
    goal: str
    memory_path: str | None = None
    branch_or_pr: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return memory_boundary_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return memory_boundary_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": memory_boundary_service.rules()}


@router.post("/classify-note")
def classify_note(request: ClassifyNoteRequest) -> dict[str, Any]:
    return memory_boundary_service.classify_note(title=request.title, body=request.body)


@router.post("/ai-handoff-template")
def ai_handoff_template(request: AiHandoffTemplateRequest) -> dict[str, Any]:
    return memory_boundary_service.ai_handoff_template(
        project=request.project,
        repo=request.repo,
        goal=request.goal,
        memory_path=request.memory_path,
        branch_or_pr=request.branch_or_pr,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return {
        "status": memory_boundary_service.status(),
        "panel": memory_boundary_service.panel(),
        "rules": memory_boundary_service.rules(),
    }
