from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.playbook_templates_library_service import playbook_templates_library_service


router = APIRouter(prefix="/api/playbook-templates", tags=["playbook-templates"])


class TemplateRequest(BaseModel):
    template_id: str
    overrides: dict[str, Any] = Field(default_factory=dict)
    goal_id: str | None = None
    operator_approved: bool = False
    simulate: bool = True


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return playbook_templates_library_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return playbook_templates_library_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": playbook_templates_library_service.rules()}


@router.get("/templates")
def templates(tag: str | None = Query(default=None), project: str | None = Query(default=None)) -> dict[str, Any]:
    return playbook_templates_library_service.templates(tag=tag, project=project)


@router.get("/templates/{template_id}")
def get_template(template_id: str) -> dict[str, Any]:
    return playbook_templates_library_service.get_template(template_id=template_id)


@router.post("/template")
def get_template_with_overrides(request: TemplateRequest) -> dict[str, Any]:
    return playbook_templates_library_service.get_template(template_id=request.template_id, overrides=request.overrides)


@router.post("/to-pipeline")
def to_pipeline(request: TemplateRequest) -> dict[str, Any]:
    return playbook_templates_library_service.to_pipeline(
        template_id=request.template_id,
        overrides=request.overrides,
        goal_id=request.goal_id,
        operator_approved=request.operator_approved,
    )


@router.post("/run")
def run_template(request: TemplateRequest) -> dict[str, Any]:
    return playbook_templates_library_service.run_template(
        template_id=request.template_id,
        overrides=request.overrides,
        goal_id=request.goal_id,
        operator_approved=request.operator_approved,
        simulate=request.simulate,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return playbook_templates_library_service.package()
