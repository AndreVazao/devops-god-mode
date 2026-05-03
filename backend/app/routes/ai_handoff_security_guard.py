from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_handoff_security_guard_service import ai_handoff_security_guard_service


router = APIRouter(prefix="/api/ai-handoff-security-guard", tags=["ai-handoff-security-guard"])


class SecurityTextRequest(BaseModel):
    text: str
    provider: str | None = None
    purpose: str | None = None


class PreparePackageRequest(BaseModel):
    text: str
    provider: str | None = None
    purpose: str | None = None
    project: str | None = None
    repo: str | None = None
    include_original: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ai_handoff_security_guard_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ai_handoff_security_guard_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": ai_handoff_security_guard_service.rules()}


@router.post("/analyze")
def analyze(request: SecurityTextRequest) -> dict[str, Any]:
    return ai_handoff_security_guard_service.analyze(
        text=request.text,
        provider=request.provider,
        purpose=request.purpose,
    )


@router.post("/sanitize")
def sanitize(request: SecurityTextRequest) -> dict[str, Any]:
    return ai_handoff_security_guard_service.sanitize(
        text=request.text,
        provider=request.provider,
        purpose=request.purpose,
    )


@router.post("/prepare")
def prepare(request: PreparePackageRequest) -> dict[str, Any]:
    return ai_handoff_security_guard_service.prepare_package(
        text=request.text,
        provider=request.provider,
        purpose=request.purpose,
        project=request.project,
        repo=request.repo,
        include_original=request.include_original,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return ai_handoff_security_guard_service.package()
