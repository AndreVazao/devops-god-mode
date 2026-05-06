from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.github_repo_inventory_feed_service import github_repo_inventory_feed_service

router = APIRouter(prefix="/api/github-repo-inventory-feed", tags=["github-repo-inventory-feed"])


class ImportConnectorSnapshotRequest(BaseModel):
    repositories: list[dict[str, Any]]
    source: str = "github_connector"
    tenant_id: str = "owner-andre"
    feed_scanner: bool = True
    auto_apply_high_confidence: bool = False


class ImportRepoNamesRequest(BaseModel):
    repo_full_names: list[str]
    source: str = "manual_paste"
    tenant_id: str = "owner-andre"
    feed_scanner: bool = True
    auto_apply_high_confidence: bool = False


class CreateCardsRequest(BaseModel):
    snapshot_id: str | None = None
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return github_repo_inventory_feed_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return github_repo_inventory_feed_service.policy()


@router.post("/import-connector-snapshot")
def import_connector_snapshot(payload: ImportConnectorSnapshotRequest) -> dict[str, Any]:
    return github_repo_inventory_feed_service.import_connector_snapshot(
        repositories=payload.repositories,
        source=payload.source,
        tenant_id=payload.tenant_id,
        feed_scanner=payload.feed_scanner,
        auto_apply_high_confidence=payload.auto_apply_high_confidence,
    )


@router.post("/import-repo-names")
def import_repo_names(payload: ImportRepoNamesRequest) -> dict[str, Any]:
    return github_repo_inventory_feed_service.import_repo_names(
        repo_full_names=payload.repo_full_names,
        source=payload.source,
        tenant_id=payload.tenant_id,
        feed_scanner=payload.feed_scanner,
        auto_apply_high_confidence=payload.auto_apply_high_confidence,
    )


@router.post("/seed-connector-seen")
def seed_connector_seen(tenant_id: str = "owner-andre", feed_scanner: bool = True, auto_apply_high_confidence: bool = True) -> dict[str, Any]:
    return github_repo_inventory_feed_service.seed_from_connector_sample(
        tenant_id=tenant_id,
        feed_scanner=feed_scanner,
        auto_apply_high_confidence=auto_apply_high_confidence,
    )


@router.post("/create-new-repo-cards")
def create_new_repo_cards(payload: CreateCardsRequest) -> dict[str, Any]:
    return github_repo_inventory_feed_service.create_new_repo_cards(
        snapshot_id=payload.snapshot_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return github_repo_inventory_feed_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return github_repo_inventory_feed_service.package()
