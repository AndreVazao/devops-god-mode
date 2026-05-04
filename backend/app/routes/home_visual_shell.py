from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.home_visual_shell_service import home_visual_shell_service

router = APIRouter(tags=["home-visual-shell"])


@router.get("/app/home", response_class=HTMLResponse)
def app_home() -> HTMLResponse:
    return HTMLResponse(home_visual_shell_service.html())


@router.get("/api/home-visual-shell/page", response_class=HTMLResponse)
def page() -> HTMLResponse:
    return HTMLResponse(home_visual_shell_service.html())


@router.get("/api/home-visual-shell/status")
@router.post("/api/home-visual-shell/status")
def status() -> dict[str, Any]:
    return home_visual_shell_service.status()


@router.get("/api/home-visual-shell/package")
@router.post("/api/home-visual-shell/package")
def package() -> dict[str, Any]:
    return home_visual_shell_service.package()
