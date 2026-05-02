from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.ruflo_research_lab_service import ruflo_research_lab_service


router = APIRouter(prefix="/api/ruflo-research-lab", tags=["ruflo-research-lab"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ruflo_research_lab_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ruflo_research_lab_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return ruflo_research_lab_service.policy()


@router.get("/mapping")
@router.post("/mapping")
def mapping() -> dict[str, Any]:
    return ruflo_research_lab_service.mapping()


@router.get("/extraction-plan")
@router.post("/extraction-plan")
def extraction_plan() -> dict[str, Any]:
    return ruflo_research_lab_service.extraction_plan()


@router.get("/reusable-registry-seed")
@router.post("/reusable-registry-seed")
def reusable_registry_seed() -> dict[str, Any]:
    return ruflo_research_lab_service.reusable_registry_seed()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return ruflo_research_lab_service.package()
