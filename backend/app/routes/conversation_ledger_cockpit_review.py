from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation_ledger_cockpit_review_service import conversation_ledger_cockpit_review_service

router = APIRouter(prefix="/api/conversation-ledger-cockpit-review", tags=["conversation-ledger-cockpit-review"])


class ProjectRequest(BaseModel):
    project_key: str = "GOD_MODE"


class CardsRequest(BaseModel):
    project_key: str = "GOD_MODE"
    include_closed: bool = False


class ReviewRequest(BaseModel):
    request_id: str
    decision: str
    project_key: str = "GOD_MODE"
    operator_note: str | None = None
    evidence_ref: str | None = None
    migration_note: str | None = None
    priority: str | None = None


class BatchReviewRequest(BaseModel):
    project_key: str = "GOD_MODE"
    reviews: list[dict[str, Any]]


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.policy()


@router.post("/cards")
def cards(payload: CardsRequest) -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.build_cards(
        project_key=payload.project_key,
        include_closed=payload.include_closed,
    )


@router.post("/review")
def review(payload: ReviewRequest) -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.review_requirement(
        request_id=payload.request_id,
        decision=payload.decision,
        project_key=payload.project_key,
        operator_note=payload.operator_note,
        evidence_ref=payload.evidence_ref,
        migration_note=payload.migration_note,
        priority=payload.priority,
    )


@router.post("/batch-review")
def batch_review(payload: BatchReviewRequest) -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.batch_review(
        project_key=payload.project_key,
        reviews=payload.reviews,
    )


@router.post("/summary")
def summary(payload: ProjectRequest) -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.summary(project_key=payload.project_key)


@router.get("/history")
@router.post("/history")
def history(project_key: str | None = None, limit: int = 50) -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.review_history(project_key=project_key, limit=limit)


@router.get("/package")
@router.post("/package")
def package(project_key: str = "GOD_MODE") -> dict[str, Any]:
    return conversation_ledger_cockpit_review_service.package(project_key=project_key)
