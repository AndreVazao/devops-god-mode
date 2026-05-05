from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.smol_godmode_reference_adapter_service import smol_godmode_reference_adapter_service

router = APIRouter(prefix="/api/smol-godmode-reference-adapter", tags=["smol-godmode-reference-adapter"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.status()


@router.get("/capability-fit")
@router.post("/capability-fit")
def capability_fit() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.capability_fit()


@router.get("/patterns")
@router.post("/patterns")
def patterns() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.extracted_patterns()


@router.get("/provider-pane-manifest")
@router.post("/provider-pane-manifest")
def provider_pane_manifest() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.provider_pane_manifest()


@router.get("/prompt-broadcast-contract")
@router.post("/prompt-broadcast-contract")
def prompt_broadcast_contract() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.prompt_broadcast_contract()


@router.get("/prompt-critic-policy")
@router.post("/prompt-critic-policy")
def prompt_critic_policy() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.prompt_critic_policy()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return smol_godmode_reference_adapter_service.package()
