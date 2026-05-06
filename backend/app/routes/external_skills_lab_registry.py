from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_skills_lab_registry_service import external_skills_lab_registry_service

router = APIRouter(prefix="/api/external-skills-lab-registry", tags=["external-skills-lab-registry"])


class RepoAssessmentPayload(BaseModel):
    repo_full_name: str
    description: str = ""
    operator_goal: str = ""
    tenant_id: str = "owner-andre"


class RepoBatchPayload(BaseModel):
    repositories: list[dict[str, Any]]
    operator_goal: str = ""
    tenant_id: str = "owner-andre"


class ReusePayload(BaseModel):
    operator_request: str
    target_project: str = "GOD_MODE"
    target_area: str = "auto"
    tenant_id: str = "owner-andre"


class IdPayload(BaseModel):
    id: str
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return external_skills_lab_registry_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return external_skills_lab_registry_service.policy()


@router.post("/seed-defaults")
def seed_defaults() -> dict[str, Any]:
    return external_skills_lab_registry_service.seed_defaults()


@router.get("/labs")
def labs(category: str | None = None) -> dict[str, Any]:
    return external_skills_lab_registry_service.list_labs(category=category)


@router.post("/assess-repo")
def assess_repo(payload: RepoAssessmentPayload) -> dict[str, Any]:
    return external_skills_lab_registry_service.assess_external_repo(
        repo_full_name=payload.repo_full_name,
        description=payload.description,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.post("/catalog-repos")
def catalog_repos(payload: RepoBatchPayload) -> dict[str, Any]:
    return external_skills_lab_registry_service.catalog_external_repos(
        repositories=payload.repositories,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.post("/decide-reuse")
def decide_reuse(payload: ReusePayload) -> dict[str, Any]:
    return external_skills_lab_registry_service.decide_reuse(
        operator_request=payload.operator_request,
        target_project=payload.target_project,
        target_area=payload.target_area,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-reuse-plan")
def create_reuse_plan(payload: IdPayload) -> dict[str, Any]:
    return external_skills_lab_registry_service.create_reuse_plan(
        decision_id=payload.id,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-lab-creation-plan")
def create_lab_creation_plan(payload: IdPayload) -> dict[str, Any]:
    return external_skills_lab_registry_service.create_lab_creation_plan(
        assessment_id=payload.id,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return external_skills_lab_registry_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return external_skills_lab_registry_service.package()
