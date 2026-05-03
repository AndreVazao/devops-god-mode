from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agent_roles_registry_service import agent_roles_registry_service


router = APIRouter(prefix="/api/agent-roles", tags=["agent-roles"])


class AssignRolesRequest(BaseModel):
    goal: str
    tags: list[str] = Field(default_factory=list)
    project: str | None = None
    repo: str | None = None
    context: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return agent_roles_registry_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return agent_roles_registry_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": agent_roles_registry_service.rules()}


@router.get("/roles")
def roles() -> dict[str, Any]:
    return agent_roles_registry_service.roles()


@router.get("/roles/{role_id}")
def get_role(role_id: str) -> dict[str, Any]:
    return agent_roles_registry_service.get_role(role_id=role_id)


@router.post("/assign")
def assign(request: AssignRolesRequest) -> dict[str, Any]:
    return agent_roles_registry_service.assign(
        goal=request.goal,
        tags=request.tags,
        project=request.project,
        repo=request.repo,
        context=request.context,
    )


@router.post("/execution-plan")
def execution_plan(request: AssignRolesRequest) -> dict[str, Any]:
    return agent_roles_registry_service.execution_plan(
        goal=request.goal,
        tags=request.tags,
        project=request.project,
        repo=request.repo,
        context=request.context,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return agent_roles_registry_service.package()
