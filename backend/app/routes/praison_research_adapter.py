from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.praison_research_adapter_service import praison_research_adapter_service


router = APIRouter(prefix="/api/praison-research", tags=["praison-research"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return praison_research_adapter_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return praison_research_adapter_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": praison_research_adapter_service.rules()}


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return praison_research_adapter_service.policy()


@router.get("/mapping")
@router.post("/mapping")
def mapping() -> dict[str, Any]:
    return praison_research_adapter_service.mapping()


@router.get("/extraction-plan")
@router.post("/extraction-plan")
def extraction_plan() -> dict[str, Any]:
    return praison_research_adapter_service.extraction_plan()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return praison_research_adapter_service.package()
