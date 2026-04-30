from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.ai_handoff_trace_ledger_service import ai_handoff_trace_ledger_service


router = APIRouter(prefix="/api/ai-handoff-trace", tags=["ai-handoff-trace"])


class PrepareHandoffRequest(BaseModel):
    project_id: str = Field(default="GOD_MODE")
    task: str = Field(default="Continuar o projeto com segurança.")
    provider: str = Field(default="chatgpt")
    target_repo: str | None = None
    operator_note: str | None = None


class RecordResultRequest(BaseModel):
    trace_id: str
    provider: str = Field(default="chatgpt")
    project_id: str = Field(default="GOD_MODE")
    summary: str
    outcome: str = Field(default="received")
    target_repo: str | None = None
    branch: str | None = None
    pr_number: int | None = None
    commit_sha: str | None = None
    memory_delta: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.policy()


@router.post("/prepare")
async def prepare(request: PrepareHandoffRequest) -> dict[str, Any]:
    return await ai_handoff_trace_ledger_service.prepare_handoff(
        project_id=request.project_id,
        task=request.task,
        provider=request.provider,
        target_repo=request.target_repo,
        operator_note=request.operator_note,
    )


@router.post("/record-result")
def record_result(request: RecordResultRequest) -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.record_result(
        trace_id=request.trace_id,
        provider=request.provider,
        project_id=request.project_id,
        summary=request.summary,
        outcome=request.outcome,
        target_repo=request.target_repo,
        branch=request.branch,
        pr_number=request.pr_number,
        commit_sha=request.commit_sha,
        memory_delta=request.memory_delta,
    )


@router.get("/ledger")
def ledger(
    limit: int = Query(default=50, ge=1, le=200),
    project_id: str | None = Query(default=None),
) -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.ledger(limit=limit, project_id=project_id)


@router.get("/trace/{trace_id}")
def trace(trace_id: str) -> dict[str, Any]:
    return ai_handoff_trace_ledger_service.trace(trace_id)


@router.get("/repo-hints/{project_id}")
def repo_hints(project_id: str) -> dict[str, Any]:
    return {"ok": True, "project_id": project_id, "repo_hints": ai_handoff_trace_ledger_service.repo_hints(project_id)}


@router.get("/package")
@router.post("/package")
async def package() -> dict[str, Any]:
    return await ai_handoff_trace_ledger_service.package()
