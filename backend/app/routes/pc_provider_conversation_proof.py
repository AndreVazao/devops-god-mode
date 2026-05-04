from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.pc_provider_conversation_proof_service import pc_provider_conversation_proof_service

router = APIRouter(prefix="/api/pc-provider-conversation-proof", tags=["pc-provider-conversation-proof"])


class ProofCommandRequest(BaseModel):
    provider: str = "chatgpt"
    url: str | None = None
    wait_login_seconds: int = 90


class ImportProofRequest(BaseModel):
    proof_file: str
    tenant_id: str = "owner-andre"
    project_hint: str | None = None


class ImportLatestRequest(BaseModel):
    tenant_id: str = "owner-andre"
    project_hint: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return pc_provider_conversation_proof_service.status()


@router.get("/install-plan")
@router.post("/install-plan")
def install_plan() -> dict[str, Any]:
    return pc_provider_conversation_proof_service.install_plan()


@router.post("/command")
def command(payload: ProofCommandRequest) -> dict[str, Any]:
    return pc_provider_conversation_proof_service.provider_proof_command(
        provider=payload.provider,
        url=payload.url,
        wait_login_seconds=payload.wait_login_seconds,
    )


@router.get("/proofs")
@router.post("/proofs")
def proofs(limit: int = 50) -> dict[str, Any]:
    return pc_provider_conversation_proof_service.list_proofs(limit=limit)


@router.post("/import-proof")
def import_proof(payload: ImportProofRequest) -> dict[str, Any]:
    return pc_provider_conversation_proof_service.import_proof_file(
        proof_file=payload.proof_file,
        tenant_id=payload.tenant_id,
        project_hint=payload.project_hint,
    )


@router.post("/import-latest")
def import_latest(payload: ImportLatestRequest) -> dict[str, Any]:
    return pc_provider_conversation_proof_service.import_latest(
        tenant_id=payload.tenant_id,
        project_hint=payload.project_hint,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return pc_provider_conversation_proof_service.first_pc_proof_package()
