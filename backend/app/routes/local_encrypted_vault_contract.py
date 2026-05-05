from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_encrypted_vault_contract_service import local_encrypted_vault_contract_service

router = APIRouter(prefix="/api/local-encrypted-vault-contract", tags=["local-encrypted-vault-contract"])


class RegisterProjectRequest(BaseModel):
    project_id: str
    repo_full_name: str | None = None
    role: str = "app"
    notes: str | None = None


class EnvTextRequest(BaseModel):
    env_text: str
    source_name: str = "uploaded_env"
    project_hint: str | None = None
    environment_name: str = "unknown"
    store_report: bool = True


class FirstCredentialFlowRequest(BaseModel):
    project_id: str = "GOD_MODE"
    provider: str = "unknown"
    environment_name: str = "production"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return local_encrypted_vault_contract_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return local_encrypted_vault_contract_service.policy()


@router.post("/register-project")
def register_project(payload: RegisterProjectRequest) -> dict[str, Any]:
    return local_encrypted_vault_contract_service.register_project(
        project_id=payload.project_id,
        repo_full_name=payload.repo_full_name,
        role=payload.role,
        notes=payload.notes,
    )


@router.post("/classify-env-text")
def classify_env_text(payload: EnvTextRequest) -> dict[str, Any]:
    return local_encrypted_vault_contract_service.classify_env_text(
        env_text=payload.env_text,
        source_name=payload.source_name,
        project_hint=payload.project_hint,
        environment_name=payload.environment_name,
    )


@router.post("/intake-env-text")
def intake_env_text(payload: EnvTextRequest) -> dict[str, Any]:
    return local_encrypted_vault_contract_service.intake_env_text(
        env_text=payload.env_text,
        source_name=payload.source_name,
        project_hint=payload.project_hint,
        environment_name=payload.environment_name,
        store_report=payload.store_report,
    )


@router.post("/first-credential-flow")
def first_credential_flow(payload: FirstCredentialFlowRequest) -> dict[str, Any]:
    return local_encrypted_vault_contract_service.first_credential_flow(
        project_id=payload.project_id,
        provider=payload.provider,
        environment_name=payload.environment_name,
    )


@router.post("/bootstrap-project-mapping")
def bootstrap_project_mapping() -> dict[str, Any]:
    return local_encrypted_vault_contract_service.project_mapping_bootstrap()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return local_encrypted_vault_contract_service.package()
