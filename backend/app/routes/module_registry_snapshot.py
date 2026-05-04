from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.module_registry_snapshot_service import module_registry_snapshot_service

router = APIRouter(prefix="/api/module-registry-snapshot", tags=["module-registry-snapshot"])


class SearchModulesRequest(BaseModel):
    query: str
    limit: int = 50


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return module_registry_snapshot_service.status()


@router.get("/tree-status")
@router.post("/tree-status")
def tree_status() -> dict[str, Any]:
    return module_registry_snapshot_service.tree_status()


@router.get("/summary")
@router.post("/summary")
def summary() -> dict[str, Any]:
    return module_registry_snapshot_service.category_summary()


@router.get("/snapshot")
@router.post("/snapshot")
def snapshot(include_items: bool = True) -> dict[str, Any]:
    return module_registry_snapshot_service.snapshot(include_items=include_items)


@router.post("/search")
def search(payload: SearchModulesRequest) -> dict[str, Any]:
    return module_registry_snapshot_service.search_modules(query=payload.query, limit=payload.limit)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return module_registry_snapshot_service.package()
