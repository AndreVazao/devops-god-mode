from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.pr_checks_visibility_service import pr_checks_visibility_service

router = APIRouter(prefix="/api/pr-checks-visibility", tags=["pr-checks-visibility"])


class PRChecksVisibilityRequest(BaseModel):
    pr: Dict[str, Any]
    workflow_runs: List[Dict[str, Any]] = Field(default_factory=list)
    statuses: List[Dict[str, Any]] = Field(default_factory=list)


@router.get('/status')
async def status():
    return pr_checks_visibility_service.get_status()


@router.get('/package')
async def package():
    return pr_checks_visibility_service.get_package()


@router.get('/demo')
async def demo():
    return pr_checks_visibility_service.demo_scenarios()


@router.post('/classify')
async def classify(payload: PRChecksVisibilityRequest):
    return pr_checks_visibility_service.classify(
        pr=payload.pr,
        workflow_runs=payload.workflow_runs,
        statuses=payload.statuses,
    )
