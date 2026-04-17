from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.patch_apply_preview_service import patch_apply_preview_service

router = APIRouter(prefix="/api/patch-apply-preview", tags=["patch-apply-preview"])


class PatchPreviewCreateRequest(BaseModel):
    patch_id: str
    apply_mode: str = Field(default="simulate_only", examples=["simulate_only"])


class PatchPreviewSimulateRequest(BaseModel):
    validation_status: str = Field(default="pending", examples=["pending"])


@router.get("/status")
async def patch_apply_preview_status():
    queue = patch_apply_preview_service.list_previews()
    return {
        "ok": True,
        "mode": "patch_apply_preview_status",
        "count": queue["count"],
        "storage": str(patch_apply_preview_service.storage_path),
    }


@router.get("/previews")
async def patch_apply_preview_list():
    return patch_apply_preview_service.list_previews()


@router.get("/previews/{preview_id}")
async def patch_apply_preview_get(preview_id: str):
    item = patch_apply_preview_service.get_preview(preview_id)
    if not item:
        raise HTTPException(status_code=404, detail="preview_not_found")
    return {"ok": True, "preview": item}


@router.post("/previews")
async def patch_apply_preview_create(payload: PatchPreviewCreateRequest):
    try:
        item = patch_apply_preview_service.create_preview(**payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=404, detail="patch_not_found")
    except PermissionError:
        raise HTTPException(status_code=409, detail="patch_not_ready_to_preview")
    return {"ok": True, "mode": "patch_apply_preview_created", "preview": item}


@router.post("/previews/{preview_id}/simulate-apply")
async def patch_apply_preview_simulate(preview_id: str, payload: PatchPreviewSimulateRequest):
    try:
        item = patch_apply_preview_service.mark_simulated_apply(preview_id, payload.validation_status)
    except ValueError:
        raise HTTPException(status_code=404, detail="preview_not_found")
    return {"ok": True, "mode": "patch_apply_simulated", "preview": item}


@router.post("/previews/{preview_id}/mark-validated")
async def patch_apply_preview_validate(preview_id: str):
    try:
        item = patch_apply_preview_service.mark_validated(preview_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="preview_not_found")
    return {"ok": True, "mode": "patch_apply_validated", "preview": item}
