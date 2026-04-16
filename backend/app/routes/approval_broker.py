from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.approval_broker_service import approval_broker_service

router = APIRouter(prefix="/api/approval-broker", tags=["approval-broker"])


class ApprovalCreateRequest(BaseModel):
    source: str = Field(..., examples=["browser_orchestration"])
    action_type: str = Field(..., examples=["connector_permission"])
    risk_level: str = Field(..., examples=["high"])
    summary: str
    details: Optional[Dict[str, Any]] = None
    requires_manual_confirmation: bool = True
    suggested_response: str = "ALTERA"
    allowed_responses: Optional[list[str]] = None


class ApprovalRespondRequest(BaseModel):
    response: str = Field(..., examples=["OK"])
    note: str = ""


@router.get("/status")
async def approval_broker_status():
    pending = approval_broker_service.list_requests(status="pending")
    return {
        "ok": True,
        "mode": "approval_broker_status",
        "pending_count": pending["count"],
        "storage": str(approval_broker_service.storage_path),
    }


@router.get("/requests")
async def approval_broker_requests(status: Optional[str] = None):
    return approval_broker_service.list_requests(status=status)


@router.get("/requests/{request_id}")
async def approval_broker_request(request_id: str):
    item = approval_broker_service.get_request(request_id)
    if not item:
        raise HTTPException(status_code=404, detail="approval_request_not_found")
    return {"ok": True, "request": item}


@router.post("/requests")
async def approval_broker_create(payload: ApprovalCreateRequest):
    item = approval_broker_service.create_request(**payload.model_dump())
    return {
        "ok": True,
        "mode": "approval_request_created",
        "request": item,
    }


@router.post("/requests/{request_id}/respond")
async def approval_broker_respond(request_id: str, payload: ApprovalRespondRequest):
    try:
        item = approval_broker_service.respond(
            request_id=request_id,
            response=payload.response,
            note=payload.note,
        )
    except ValueError as exc:
        detail = str(exc)
        if detail == "request_not_found":
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)

    return {
        "ok": True,
        "mode": "approval_request_updated",
        "request": item,
    }
