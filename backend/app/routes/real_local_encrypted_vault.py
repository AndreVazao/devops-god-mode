from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.real_local_encrypted_vault_service import real_local_encrypted_vault_service

router = APIRouter(prefix="/api/real-local-encrypted-vault", tags=["real-local-encrypted-vault"])


class WriteGateRequest(BaseModel):
    secret_ref_id: str
    project_id: str
    provider: str
    environment: str
    key_name: str
    risk_level: str = "high"


class ReadGateRequest(BaseModel):
    secret_ref_id: str
    purpose: str
    risk_level: str = "high"


class StoreSecretRequest(BaseModel):
    secret_ref_id: str
    secret_value: str
    passphrase: str
    project_id: str
    provider: str
    environment: str
    key_name: str
    approved_gate_id: str
    notes: str | None = None


class ReadSecretRequest(BaseModel):
    secret_ref_id: str
    passphrase: str
    approved_gate_id: str
    purpose: str
    reveal: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return real_local_encrypted_vault_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return real_local_encrypted_vault_service.policy()


@router.post("/create-write-gate")
def create_write_gate(payload: WriteGateRequest) -> dict[str, Any]:
    return real_local_encrypted_vault_service.create_write_gate(
        secret_ref_id=payload.secret_ref_id,
        project_id=payload.project_id,
        provider=payload.provider,
        environment=payload.environment,
        key_name=payload.key_name,
        risk_level=payload.risk_level,
    )


@router.post("/create-read-gate")
def create_read_gate(payload: ReadGateRequest) -> dict[str, Any]:
    return real_local_encrypted_vault_service.create_read_gate(
        secret_ref_id=payload.secret_ref_id,
        purpose=payload.purpose,
        risk_level=payload.risk_level,
    )


@router.post("/store-secret")
def store_secret(payload: StoreSecretRequest) -> dict[str, Any]:
    return real_local_encrypted_vault_service.store_secret(
        secret_ref_id=payload.secret_ref_id,
        secret_value=payload.secret_value,
        passphrase=payload.passphrase,
        project_id=payload.project_id,
        provider=payload.provider,
        environment=payload.environment,
        key_name=payload.key_name,
        approved_gate_id=payload.approved_gate_id,
        notes=payload.notes,
    )


@router.post("/read-secret")
def read_secret(payload: ReadSecretRequest) -> dict[str, Any]:
    return real_local_encrypted_vault_service.read_secret(
        secret_ref_id=payload.secret_ref_id,
        passphrase=payload.passphrase,
        approved_gate_id=payload.approved_gate_id,
        purpose=payload.purpose,
        reveal=payload.reveal,
    )


@router.get("/entries")
@router.post("/entries")
def entries() -> dict[str, Any]:
    return real_local_encrypted_vault_service.list_entries()


@router.get("/audit")
@router.post("/audit")
def audit(limit: int = 50) -> dict[str, Any]:
    return real_local_encrypted_vault_service.audit_log(limit=limit)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return real_local_encrypted_vault_service.package()
