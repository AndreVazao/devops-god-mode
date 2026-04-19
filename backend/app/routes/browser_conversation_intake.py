from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)

router = APIRouter(prefix="/api/browser-intake", tags=["browser-intake"])


class IntakeSessionCreateRequest(BaseModel):
    source_type: str = Field(..., examples=["browser_ai_conversation"])
    source_url: str
    conversation_title: str
    warnings: Optional[List[str]] = None
    project_hint: Optional[str] = None
    intake_goal: str = "capture_code_and_context"
    alias_hint: Optional[str] = None


class IntakeCaptureAppendRequest(BaseModel):
    snippets: Optional[List[Dict[str, Any]]] = None
    code_blocks: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None
    increment_scroll_steps: int = 1
    capture_status: str = "capturing"


@router.get("/status")
async def browser_intake_status():
    queue = browser_conversation_intake_service.get_priority_queue()
    return {
        "ok": True,
        "mode": "browser_conversation_intake_status",
        "count": queue["count"],
        "storage": str(browser_conversation_intake_service.storage_path),
        "next_session_id": (
            queue["sessions"][0]["session_id"] if queue["sessions"] else None
        ),
    }


@router.get("/sessions")
async def browser_intake_list():
    return browser_conversation_intake_service.list_sessions()


@router.get("/priority-queue")
async def browser_intake_priority_queue():
    return browser_conversation_intake_service.get_priority_queue()


@router.get("/next-session")
async def browser_intake_next_session():
    return browser_conversation_intake_service.get_next_session()


@router.get("/sessions/{session_id}")
async def browser_intake_get(session_id: str):
    item = browser_conversation_intake_service.get_session(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"ok": True, "session": item}


@router.get("/sessions/{session_id}/navigation-plan")
async def browser_intake_navigation_plan(session_id: str):
    try:
        return browser_conversation_intake_service.get_navigation_plan(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="session_not_found")


@router.get("/sessions/{session_id}/progress")
async def browser_intake_progress(session_id: str):
    try:
        return browser_conversation_intake_service.get_capture_progress(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="session_not_found")


@router.post("/sessions")
async def browser_intake_create(payload: IntakeSessionCreateRequest):
    item = browser_conversation_intake_service.create_session(**payload.model_dump())
    return {"ok": True, "mode": "browser_intake_session_created", "session": item}


@router.post("/seed-from-focus")
async def browser_intake_seed_from_focus():
    return browser_conversation_intake_service.seed_from_conversation_focus()


@router.post("/sessions/{session_id}/capture")
async def browser_intake_append_capture(session_id: str, payload: IntakeCaptureAppendRequest):
    try:
        item = browser_conversation_intake_service.append_capture(
            session_id=session_id, **payload.model_dump()
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"ok": True, "mode": "browser_intake_capture_appended", "session": item}
