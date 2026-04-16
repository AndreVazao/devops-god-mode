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


class IntakeCaptureAppendRequest(BaseModel):
    snippets: Optional[List[Dict[str, Any]]] = None
    code_blocks: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None
    increment_scroll_steps: int = 1
    capture_status: str = "capturing"


@router.get("/status")
async def browser_intake_status():
    queue = browser_conversation_intake_service.list_sessions()
    return {
        "ok": True,
        "mode": "browser_conversation_intake_status",
        "count": queue["count"],
        "storage": str(browser_conversation_intake_service.storage_path),
    }


@router.get("/sessions")
async def browser_intake_list():
    return browser_conversation_intake_service.list_sessions()


@router.get("/sessions/{session_id}")
async def browser_intake_get(session_id: str):
    item = browser_conversation_intake_service.get_session(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"ok": True, "session": item}


@router.post("/sessions")
async def browser_intake_create(payload: IntakeSessionCreateRequest):
    item = browser_conversation_intake_service.create_session(**payload.model_dump())
    return {"ok": True, "mode": "browser_intake_session_created", "session": item}


@router.post("/sessions/{session_id}/capture")
async def browser_intake_append_capture(session_id: str, payload: IntakeCaptureAppendRequest):
    try:
        item = browser_conversation_intake_service.append_capture(session_id=session_id, **payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"ok": True, "mode": "browser_intake_capture_appended", "session": item}
