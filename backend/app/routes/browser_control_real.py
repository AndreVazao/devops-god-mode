from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.browser_control_real_service import browser_control_real_service

router = APIRouter(prefix="/api/browser-control", tags=["browser-control"])


class BrowserControlAdvanceRequest(BaseModel):
    completion_note: str = ""


@router.get("/status")
async def browser_control_status():
    controls = browser_control_real_service.get_controls()["controls"]
    return {
        "ok": True,
        "mode": "browser_control_status",
        "controls_count": len(controls),
        "control_status": "browser_control_ready",
    }


@router.get("/sessions")
async def browser_control_sessions():
    return browser_control_real_service.get_controls()


@router.get("/sessions/{control_id}/actions")
async def browser_control_actions(control_id: str):
    try:
        return browser_control_real_service.get_actions(control_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="control_not_found")


@router.get("/next-action")
async def browser_control_next_action():
    return browser_control_real_service.get_next_action()


@router.post("/sessions/{control_id}/actions/{action_id}/advance")
async def browser_control_advance_action(control_id: str, action_id: str, payload: BrowserControlAdvanceRequest):
    try:
        return browser_control_real_service.advance_action(
            control_id=control_id,
            action_id=action_id,
            completion_note=payload.completion_note,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="control_not_found")
