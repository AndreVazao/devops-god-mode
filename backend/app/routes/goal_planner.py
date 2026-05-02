from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.goal_planner_service import goal_planner_service


router = APIRouter(prefix="/api/goal-planner", tags=["goal-planner"])


class GoalPlanRequest(BaseModel):
    goal: str
    project: str | None = None
    repo: str | None = None
    context: str | None = None
    priority: str = "normal"
    execution_mode: str = "safe_autopilot"
    constraints: list[str] = Field(default_factory=list)


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return goal_planner_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return goal_planner_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": goal_planner_service.rules()}


@router.get("/template")
def template() -> dict[str, Any]:
    return goal_planner_service.template()


@router.get("/policy")
def policy() -> dict[str, Any]:
    return goal_planner_service.policy()


@router.post("/plan")
def plan(request: GoalPlanRequest) -> dict[str, Any]:
    return goal_planner_service.create_plan(
        goal=request.goal,
        project=request.project,
        repo=request.repo,
        context=request.context,
        priority=request.priority,
        execution_mode=request.execution_mode,
        constraints=request.constraints,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return goal_planner_service.package()
