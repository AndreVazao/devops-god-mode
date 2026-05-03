from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.pipeline_persistence_executor_service import pipeline_persistence_executor_service


router = APIRouter(prefix="/api/pipeline-store", tags=["pipeline-store"])


class SavePipelineRequest(BaseModel):
    pipeline: dict[str, Any] = Field(default_factory=dict)
    source: str = "manual"


class CreateFromGoalRequest(BaseModel):
    goal: str
    project: str | None = None
    repo: str | None = None
    context: str | None = None
    priority: str = "normal"
    sensitive: bool = False
    needs_code: bool = False
    preferred_provider: str | None = None


class ExecuteRequest(BaseModel):
    pipeline_id: str
    dry_run: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return pipeline_persistence_executor_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return pipeline_persistence_executor_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": pipeline_persistence_executor_service.rules()}


@router.post("/save")
def save(request: SavePipelineRequest) -> dict[str, Any]:
    return pipeline_persistence_executor_service.save_pipeline(pipeline=request.pipeline, source=request.source)


@router.post("/create-from-goal")
def create_from_goal(request: CreateFromGoalRequest) -> dict[str, Any]:
    return pipeline_persistence_executor_service.create_and_save_from_goal(
        goal=request.goal,
        project=request.project,
        repo=request.repo,
        context=request.context,
        priority=request.priority,
        sensitive=request.sensitive,
        needs_code=request.needs_code,
        preferred_provider=request.preferred_provider,
    )


@router.get("/list")
def list_pipelines(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    return pipeline_persistence_executor_service.list_pipelines(limit=limit)


@router.get("/load/{pipeline_id}")
def load(pipeline_id: str) -> dict[str, Any]:
    return pipeline_persistence_executor_service.load_pipeline(pipeline_id=pipeline_id)


@router.post("/execute-low-risk")
def execute_low_risk(request: ExecuteRequest) -> dict[str, Any]:
    return pipeline_persistence_executor_service.execute_low_risk(pipeline_id=request.pipeline_id, dry_run=request.dry_run)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return pipeline_persistence_executor_service.package()
