from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.approval_gated_execution_service import approval_gated_execution_service

router = APIRouter(prefix="/api/execution-gate", tags=["execution-gate"])


class SensitiveExecutionCreateRequest(BaseModel):
    action_type: str = Field(..., examples=["replace_critical_file"])
    risk_level: str = Field(..., examples=["high"])
    summary: str
    repo_full_name: Optional[str] = None
    target_path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@router.get("/status")
async def execution_gate_status():
    waiting = approval_gated_execution_service.list_executions(status="waiting_for_approval")
    return {
        "ok": True,
        "mode": "execution_gate_status",
        "waiting_count": waiting["count"],
        "storage": str(approval_gated_execution_service.storage_path),
    }


@router.get("/executions")
async def execution_gate_list(status: Optional[str] = None):
    return approval_gated_execution_service.list_executions(status=status)


@router.get("/executions/{execution_id}")
async def execution_gate_get(execution_id: str):
    item = approval_gated_execution_service.get_execution(execution_id)
    if not item:
        raise HTTPException(status_code=404, detail="execution_not_found")
    return {"ok": True, "execution": item}


@router.post("/executions")
async def execution_gate_create(payload: SensitiveExecutionCreateRequest):
    item = approval_gated_execution_service.create_sensitive_execution(**payload.model_dump())
    return {"ok": True, "mode": "execution_created_waiting_for_approval", "execution": item}


@router.post("/executions/{execution_id}/sync")
async def execution_gate_sync(execution_id: str):
    try:
        item = approval_gated_execution_service.sync_with_approval(execution_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="execution_not_found")
    return {"ok": True, "mode": "execution_synced", "execution": item}
