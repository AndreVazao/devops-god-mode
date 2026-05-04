from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.github_approved_actions_executor_service import github_approved_actions_executor_service

router = APIRouter(prefix="/api/github-approved-actions", tags=["github-approved-actions"])


class ExecuteApprovedGitHubPatchRequest(BaseModel):
    plan_id: str
    approval_phrase: str = ""
    pr_title: str | None = None
    pr_body: str | None = None
    draft_pr: bool = False
    dry_run: bool = True


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return github_approved_actions_executor_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return github_approved_actions_executor_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return github_approved_actions_executor_service.policy()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": github_approved_actions_executor_service.rules()}


@router.post("/execute")
async def execute(request: ExecuteApprovedGitHubPatchRequest) -> dict[str, Any]:
    return await github_approved_actions_executor_service.execute(
        plan_id=request.plan_id,
        approval_phrase=request.approval_phrase,
        pr_title=request.pr_title,
        pr_body=request.pr_body,
        draft_pr=request.draft_pr,
        dry_run=request.dry_run,
    )


@router.get("/latest")
@router.post("/latest")
def latest() -> dict[str, Any]:
    return github_approved_actions_executor_service.latest()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return github_approved_actions_executor_service.package()
