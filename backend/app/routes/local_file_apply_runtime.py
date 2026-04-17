from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.local_file_apply_runtime_service import local_file_apply_runtime_service

router = APIRouter(prefix="/api/local-file-apply-runtime", tags=["local-file-apply-runtime"])


class LocalFileApplyCreateRequest(BaseModel):
    patch_id: str
    preview_id: str
    local_repo_path: str
    local_target_file: str
    execution_mode: str = Field(default="simulate_local_write", examples=["simulate_local_write"])


class LocalFileApplyValidateRequest(BaseModel):
    validation_result: str = Field(default="passed", examples=["passed"])


@router.get("/status")
async def local_file_apply_status():
    queue = local_file_apply_runtime_service.list_apply_runs()
    return {
        "ok": True,
        "mode": "local_file_apply_runtime_status",
        "count": queue["count"],
        "storage": str(local_file_apply_runtime_service.storage_path),
    }


@router.get("/runs")
async def local_file_apply_list():
    return local_file_apply_runtime_service.list_apply_runs()


@router.get("/runs/{apply_run_id}")
async def local_file_apply_get(apply_run_id: str):
    item = local_file_apply_runtime_service.get_apply_run(apply_run_id)
    if not item:
        raise HTTPException(status_code=404, detail="apply_run_not_found")
    return {"ok": True, "apply_run": item}


@router.post("/runs")
async def local_file_apply_create(payload: LocalFileApplyCreateRequest):
    try:
        item = local_file_apply_runtime_service.create_apply_run(**payload.model_dump())
    except ValueError as exc:
        detail = str(exc)
        raise HTTPException(status_code=404 if detail in {"patch_not_found", "preview_not_found"} else 409, detail=detail)
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"ok": True, "mode": "local_file_apply_run_created", "apply_run": item}


@router.post("/runs/{apply_run_id}/mark-validated")
async def local_file_apply_mark_validated(apply_run_id: str, payload: LocalFileApplyValidateRequest):
    try:
        item = local_file_apply_runtime_service.mark_validated(apply_run_id, payload.validation_result)
    except ValueError:
        raise HTTPException(status_code=404, detail="apply_run_not_found")
    return {"ok": True, "mode": "local_file_apply_validated", "apply_run": item}
