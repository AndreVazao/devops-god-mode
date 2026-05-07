from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mobile_pc_pairing_remote_access_service import mobile_pc_pairing_remote_access_service

router = APIRouter(prefix="/api/mobile-pc-pairing", tags=["mobile-pc-pairing"])


class PairingPayload(BaseModel):
    tenant_id: str = "owner-andre"
    port: int = 8000
    ttl_minutes: int = 30


class RemotePlanPayload(BaseModel):
    provider: str = "cloudflare_tunnel"
    public_url: str = ""
    project_id: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


class StoreRemotePayload(BaseModel):
    remote_profile_id: str
    material: str
    label: str = "remote access material"
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.status()


@router.post("/create-pairing-session")
def create_pairing_session(payload: PairingPayload) -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.create_pairing_session(
        tenant_id=payload.tenant_id,
        port=payload.port,
        ttl_minutes=payload.ttl_minutes,
    )


@router.post("/create-remote-access-plan")
def create_remote_access_plan(payload: RemotePlanPayload) -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.create_remote_access_plan(
        provider=payload.provider,
        public_url=payload.public_url,
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )


@router.post("/store-remote-material")
def store_remote_material(payload: StoreRemotePayload) -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.store_remote_material(
        remote_profile_id=payload.remote_profile_id,
        material=payload.material,
        label=payload.label,
        tenant_id=payload.tenant_id,
    )


@router.get("/connection-manifest")
def connection_manifest(tenant_id: str = "owner-andre") -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.connection_manifest(tenant_id=tenant_id)


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return mobile_pc_pairing_remote_access_service.package()
