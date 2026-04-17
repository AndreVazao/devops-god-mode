from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.write_verify_rollback_service import write_verify_rollback_service

router = APIRouter(prefix="/api/write-verify-rollback", tags=["write-verify-rollback"])


class VerifyRunCreateRequest(BaseModel):
    write_run_id: str
    verification_mode: str = Field(default="post_write_local_checks", examples=["post_write_local_checks"])
    verification_checks: list[str] | None = None


@router.get("/status")
async def write_verify_status():
    queue = write_verify_rollback_service.list_verify_runs()
    return {
        "ok": True,
        "mode": "write_verify_rollback_status",
        "count": queue["count"],
        "storage": str(write_verify_rollback_service.storage_path),
    }


@router.get("/runs")
async def write_verify_list():
    return write_verify_rollback_service.list_verify_runs()


@router.get("/runs/{verify_run_id}")
async def write_verify_get(verify_run_id: str):
    item = write_verify_rollback_service.get_verify_run(verify_run_id)
    if not item:
        raise HTTPException(status_code=404, detail="verify_run_not_found")
    return {"ok": True, "verify_run": item}


@router.post("/runs")
async def write_verify_create(payload: VerifyRunCreateRequest):
    try:
        item = write_verify_rollback_service.create_verify_run(**payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=404, detail="write_run_not_found")
    return {"ok": True, "mode": "write_verify_run_created", "verify_run": item}


@router.post("/runs/{verify_run_id}/mark-passed")
async def write_verify_mark_passed(verify_run_id: str):
    try:
        item = write_verify_rollback_service.mark_verification_passed(verify_run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="verify_run_not_found")
    return {"ok": True, "mode": "write_verify_passed", "verify_run": item}


@router.post("/runs/{verify_run_id}/mark-failed")
async def write_verify_mark_failed(verify_run_id: str):
    try:
        item = write_verify_rollback_service.mark_verification_failed(verify_run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="verify_run_not_found")
    return {"ok": True, "mode": "write_verify_failed", "verify_run": item}


@router.post("/runs/{verify_run_id}/rollback")
async def write_verify_rollback(verify_run_id: str):
    try:
        item = write_verify_rollback_service.execute_rollback(verify_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"ok": True, "mode": "write_verify_rollback_executed", "verify_run": item}
