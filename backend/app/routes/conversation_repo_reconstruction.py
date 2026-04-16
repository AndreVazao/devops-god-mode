from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.conversation_repo_reconstruction_service import (
    conversation_repo_reconstruction_service,
)

router = APIRouter(prefix="/api/conversation-reconstruction", tags=["conversation-reconstruction"])


class ReconstructionCreateRequest(BaseModel):
    source_type: str = Field(..., examples=["browser_ai_conversation"])
    source_label: str
    messages_scanned: int = 0
    code_blocks_found: int = 0
    proposed_repo_name: str
    proposed_tree: List[str]
    risks: Optional[List[str]] = None
    notes: str = ""


@router.get("/status")
async def reconstruction_status():
    queue = conversation_repo_reconstruction_service.list_reconstructions()
    return {
        "ok": True,
        "mode": "conversation_reconstruction_status",
        "count": queue["count"],
        "storage": str(conversation_repo_reconstruction_service.storage_path),
    }


@router.get("/proposals")
async def reconstruction_list():
    return conversation_repo_reconstruction_service.list_reconstructions()


@router.get("/proposals/{reconstruction_id}")
async def reconstruction_get(reconstruction_id: str):
    item = conversation_repo_reconstruction_service.get_reconstruction(reconstruction_id)
    if not item:
        raise HTTPException(status_code=404, detail="reconstruction_not_found")
    return {"ok": True, "reconstruction": item}


@router.post("/proposals")
async def reconstruction_create(payload: ReconstructionCreateRequest):
    item = conversation_repo_reconstruction_service.create_proposal(**payload.model_dump())
    return {"ok": True, "mode": "conversation_reconstruction_proposal_created", "reconstruction": item}


@router.post("/proposals/{reconstruction_id}/sync")
async def reconstruction_sync(reconstruction_id: str):
    try:
        item = conversation_repo_reconstruction_service.sync_with_approval(reconstruction_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="reconstruction_not_found")
    return {"ok": True, "mode": "conversation_reconstruction_synced", "reconstruction": item}
