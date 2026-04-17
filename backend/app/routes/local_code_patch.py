from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.local_code_patch_service import local_code_patch_service

router = APIRouter(prefix="/api/local-code-patch", tags=["local-code-patch"])


class LocalCodePatchCreateRequest(BaseModel):
    repo_full_name: str
    target_path: str
    instruction: str
    patch_strategy: str = Field(..., examples=["insert_or_update_block"])
    risk_level: str = Field(..., examples=["medium"])
    proposed_changes: Optional[List[Dict[str, Any]]] = None
    validation_plan: Optional[List[str]] = None


@router.get("/status")
async def local_code_patch_status():
    queue = local_code_patch_service.list_patches()
    return {
        "ok": True,
        "mode": "local_code_patch_status",
        "count": queue["count"],
        "storage": str(local_code_patch_service.storage_path),
    }


@router.get("/patches")
async def local_code_patch_list():
    return local_code_patch_service.list_patches()


@router.get("/patches/{patch_id}")
async def local_code_patch_get(patch_id: str):
    item = local_code_patch_service.get_patch(patch_id)
    if not item:
        raise HTTPException(status_code=404, detail="patch_not_found")
    return {"ok": True, "patch": item}


@router.post("/patches")
async def local_code_patch_create(payload: LocalCodePatchCreateRequest):
    item = local_code_patch_service.create_patch(**payload.model_dump())
    return {"ok": True, "mode": "local_code_patch_created", "patch": item}


@router.post("/patches/{patch_id}/sync")
async def local_code_patch_sync(patch_id: str):
    try:
        item = local_code_patch_service.sync_with_approval(patch_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="patch_not_found")
    return {"ok": True, "mode": "local_code_patch_synced", "patch": item}
