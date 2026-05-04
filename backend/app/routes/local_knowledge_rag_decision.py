from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.local_knowledge_rag_decision_service import local_knowledge_rag_decision_service

router = APIRouter(prefix="/api/local-knowledge-rag", tags=["local-knowledge-rag"])


class BuildIndexRequest(BaseModel):
    project_name: str = "GOD_MODE"
    roots: Optional[List[Dict[str, Any]]] = None
    max_items: int = Field(default=1500, ge=1, le=1500)


class SearchRequest(BaseModel):
    query: str
    project_name: str = "GOD_MODE"
    source_types: Optional[List[str]] = None
    limit: int = Field(default=12, ge=1, le=50)
    index_id: Optional[str] = None
    build_if_missing: bool = True


class ReuseCheckRequest(BaseModel):
    capability_name: str
    target_project: str = "GOD_MODE"
    limit: int = Field(default=10, ge=1, le=50)


class DecisionRequest(BaseModel):
    goal: str
    project_name: str = "GOD_MODE"
    capability_name: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return local_knowledge_rag_decision_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return local_knowledge_rag_decision_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return local_knowledge_rag_decision_service.policy()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": local_knowledge_rag_decision_service.rules()}


@router.post("/build-index")
def build_index(request: BuildIndexRequest) -> dict[str, Any]:
    return local_knowledge_rag_decision_service.build_index(
        project_name=request.project_name,
        roots=request.roots,
        max_items=request.max_items,
    )


@router.post("/search")
def search(request: SearchRequest) -> dict[str, Any]:
    return local_knowledge_rag_decision_service.search(
        query=request.query,
        project_name=request.project_name,
        source_types=request.source_types,
        limit=request.limit,
        index_id=request.index_id,
        build_if_missing=request.build_if_missing,
    )


@router.post("/reuse-check")
def reuse_check(request: ReuseCheckRequest) -> dict[str, Any]:
    return local_knowledge_rag_decision_service.reuse_check(
        capability_name=request.capability_name,
        target_project=request.target_project,
        limit=request.limit,
    )


@router.post("/decision")
def decision(request: DecisionRequest) -> dict[str, Any]:
    return local_knowledge_rag_decision_service.decision(
        goal=request.goal,
        project_name=request.project_name,
        capability_name=request.capability_name,
        limit=request.limit,
    )


@router.get("/latest")
@router.post("/latest")
def latest() -> dict[str, Any]:
    return local_knowledge_rag_decision_service.latest()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return local_knowledge_rag_decision_service.package()
