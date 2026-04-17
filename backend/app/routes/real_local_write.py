from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.real_local_write_service import real_local_write_service

router = APIRouter(prefix="/api/real-local-write", tags=["real-local-write"])


class RealLocalWriteCreateRequest(BaseModel):
    apply_run_id: str
    write_mode: str = Field(default="real_local_write", examples=["real_local_write"])


class RealLocalWriteValidateRequest(BaseModel):
    validation_result: str = Field(default="passed", examples=["passed"])


@router.get("/status")
async def real_local_write_status():
    queue = real_local_write_service.list_write_runs()
    return {
        "ok": True,
        "mode": "real_local_write_status",
        "count": queue["count"],
        "storage": str(real_local_write_service.storage_path),
    }


@router.get("/runs")
async def real_local_write_list():
    return real_local_write_service.list_write_runs()


@router.get("/runs/{write_run_id}")
async def real_local_write_get(write_run_id: str):
    item = real_local_write_service.get_write_run(write_run_id)
    if not item:
        raise HTTPException(status_code=404, detail="write_run_not_found")
    return {"ok": True, "write_run": item}


@router.post("/runs")
async def real_local_write_create(payload: RealLocalWriteCreateRequest):
    try:
        item = real_local_write_service.create_real_write(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"ok": True, "mode": "real_local_write_created", "write_run": item}


@router.post("/runs/{write_run_id}/restore")
async def real_local_write_restore(write_run_id: str):
    try:
        item = real_local_write_service.restore_backup(write_run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="write_run_not_found")
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"ok": True, "mode": "real_local_write_restored", "write_run": item}


@router.post("/runs/{write_run_id}/mark-validated")
async def real_local_write_mark_validated(write_run_id: str, payload: RealLocalWriteValidateRequest):
    try:
        item = real_local_write_service.mark_validated(write_run_id, payload.validation_result)
    except ValueError:
        raise HTTPException(status_code=404, detail="write_run_not_found")
    return {"ok": True, "mode": "real_local_write_validated", "write_run": item}
