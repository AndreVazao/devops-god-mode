from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services.app_entrypoint_manifest_service import app_entrypoint_manifest_service

router = APIRouter(tags=["app-entrypoint-manifest"])


def _home_redirect() -> RedirectResponse:
    return RedirectResponse(url=app_entrypoint_manifest_service.CANONICAL_ROUTE, status_code=307)


@router.get("/app")
def app_root() -> RedirectResponse:
    return _home_redirect()


@router.get("/desktop")
def desktop_root() -> RedirectResponse:
    return _home_redirect()


@router.get("/mobile")
def mobile_root() -> RedirectResponse:
    return _home_redirect()


@router.get("/home")
def home_root() -> RedirectResponse:
    return _home_redirect()


@router.get("/app/mobile")
def app_mobile() -> RedirectResponse:
    return _home_redirect()


@router.get("/app/apk-start")
def apk_start_compatibility() -> RedirectResponse:
    return _home_redirect()


@router.get("/api/app-entrypoint/status")
@router.post("/api/app-entrypoint/status")
def status() -> dict[str, Any]:
    return app_entrypoint_manifest_service.status()


@router.get("/api/app-entrypoint/aliases")
@router.post("/api/app-entrypoint/aliases")
def aliases() -> dict[str, Any]:
    return {"ok": True, "aliases": app_entrypoint_manifest_service.aliases()}


@router.get("/api/app-entrypoint/manifest")
@router.post("/api/app-entrypoint/manifest")
def manifest() -> dict[str, Any]:
    return app_entrypoint_manifest_service.manifest()


@router.get("/api/app-entrypoint/package")
@router.post("/api/app-entrypoint/package")
def package() -> dict[str, Any]:
    return app_entrypoint_manifest_service.package()
