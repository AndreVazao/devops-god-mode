from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repo_scanner_real_work_map_service import repo_scanner_real_work_map_service

router = APIRouter(prefix="/api/repo-scanner-real-work-map", tags=["repo-scanner-real-work-map"])


class ScanReposRequest(BaseModel):
    repo_full_names: list[str] | None = None
    tenant_id: str = "owner-andre"
    auto_apply_high_confidence: bool = False


class SuggestRepoRequest(BaseModel):
    repo_full_name: str


class ApplySuggestionRequest(BaseModel):
    suggestion_id: str
    tenant_id: str = "owner-andre"


class ReviewCardsRequest(BaseModel):
    scan_id: str | None = None
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return repo_scanner_real_work_map_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return repo_scanner_real_work_map_service.policy()


@router.post("/scan")
def scan(payload: ScanReposRequest) -> dict[str, Any]:
    return repo_scanner_real_work_map_service.scan_repos(
        repo_full_names=payload.repo_full_names,
        tenant_id=payload.tenant_id,
        auto_apply_high_confidence=payload.auto_apply_high_confidence,
    )


@router.post("/suggest-repo")
def suggest_repo(payload: SuggestRepoRequest) -> dict[str, Any]:
    return repo_scanner_real_work_map_service.suggest_repo(repo_full_name=payload.repo_full_name)


@router.post("/apply-suggestion")
def apply_suggestion(payload: ApplySuggestionRequest) -> dict[str, Any]:
    return repo_scanner_real_work_map_service.apply_suggestion(
        suggestion_id=payload.suggestion_id,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-review-cards")
def create_review_cards(payload: ReviewCardsRequest) -> dict[str, Any]:
    return repo_scanner_real_work_map_service.create_review_cards(
        scan_id=payload.scan_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return repo_scanner_real_work_map_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return repo_scanner_real_work_map_service.package()
