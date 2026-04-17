from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.local_real_validator_service import local_real_validator_service

router = APIRouter(prefix="/api/local-real-validator", tags=["local-real-validator"])


class LocalRealValidatorCreateRequest(BaseModel):
    write_run_id: str
    validator_mode: str = Field(default="post_write_real_checks", examples=["post_write_real_checks"])
    checks: List[str] | None = None


class LocalRealValidatorObserveRequest(BaseModel):
    observed_file_excerpt: str
    checks_result: Dict[str, str]


@router.get("/status")
async def local_real_validator_status():
    queue = local_real_validator_service.list_validator_runs()
    return {
        "ok": True,
        "mode": "local_real_validator_status",
        "count": queue["count"],
        "storage": str(local_real_validator_service.storage_path),
    }


@router.get("/runs")
async def local_real_validator_list():
    return local_real_validator_service.list_validator_runs()


@router.get("/runs/{validator_run_id}")
async def local_real_validator_get(validator_run_id: str):
    item = local_real_validator_service.get_validator_run(validator_run_id)
    if not item:
        raise HTTPException(status_code=404, detail="validator_run_not_found")
    return {"ok": True, "validator_run": item}


@router.post("/runs")
async def local_real_validator_create(payload: LocalRealValidatorCreateRequest):
    try:
        item = local_real_validator_service.create_validator_run(**payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=404, detail="write_run_not_found")
    return {"ok": True, "mode": "local_real_validator_created", "validator_run": item}


@router.post("/runs/{validator_run_id}/observe")
async def local_real_validator_observe(validator_run_id: str, payload: LocalRealValidatorObserveRequest):
    try:
        item = local_real_validator_service.record_observation(
            validator_run_id,
            payload.observed_file_excerpt,
            payload.checks_result,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="validator_run_not_found")
    return {"ok": True, "mode": "local_real_validator_observed", "validator_run": item}


@router.post("/runs/{validator_run_id}/finalize")
async def local_real_validator_finalize(validator_run_id: str):
    try:
        item = local_real_validator_service.finalize_validator_run(validator_run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="validator_run_not_found")
    return {"ok": True, "mode": "local_real_validator_finalized", "validator_run": item}
