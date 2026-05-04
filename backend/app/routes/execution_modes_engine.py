from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.execution_modes_engine_service import execution_modes_engine_service


router = APIRouter(prefix="/api/execution-modes", tags=["execution-modes"])


class BuildStrategyRequest(BaseModel):
    mode: str = "sequential"
    steps: list[dict[str, Any]] = Field(default_factory=list)
    playbook: dict[str, Any] = Field(default_factory=dict)
    pipeline: dict[str, Any] = Field(default_factory=dict)
    operator_approved: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return execution_modes_engine_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return execution_modes_engine_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": execution_modes_engine_service.rules()}


@router.get("/modes")
def modes() -> dict[str, Any]:
    return execution_modes_engine_service.modes()


@router.get("/modes/{mode}")
def get_mode(mode: str) -> dict[str, Any]:
    return execution_modes_engine_service.get_mode(mode=mode)


@router.post("/build-strategy")
def build_strategy(request: BuildStrategyRequest) -> dict[str, Any]:
    return execution_modes_engine_service.build_strategy(
        mode=request.mode,
        steps=request.steps or None,
        playbook=request.playbook or None,
        pipeline=request.pipeline or None,
        operator_approved=request.operator_approved,
    )


@router.post("/simulate")
def simulate(request: BuildStrategyRequest) -> dict[str, Any]:
    return execution_modes_engine_service.simulate(
        mode=request.mode,
        steps=request.steps or None,
        playbook=request.playbook or None,
        pipeline=request.pipeline or None,
        operator_approved=request.operator_approved,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return execution_modes_engine_service.package()
