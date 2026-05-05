from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.real_work_fast_path_service import real_work_fast_path_service

router = APIRouter(prefix="/api/real-work-fast-path", tags=["real-work-fast-path"])


class ProjectGroupRequest(BaseModel):
    label: str
    aliases: list[str] | None = None
    expected_fronts: list[str] | None = None
    description: str = ""


class RepoLinkRequest(BaseModel):
    repo_full_name: str
    project_hint: str | None = None
    front: str | None = None
    evidence: str | None = None


class ConversationLinkRequest(BaseModel):
    title: str
    provider: str
    project_hint: str
    source_ref: str | None = None
    summary: str = ""


class ClassifyTextRequest(BaseModel):
    text: str


class WorkRunRequest(BaseModel):
    operator_request: str
    project_hint: str = "GOD_MODE"
    selected_provider_ids: list[str] | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return real_work_fast_path_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return real_work_fast_path_service.policy()


@router.post("/seed-defaults")
def seed_defaults() -> dict[str, Any]:
    return real_work_fast_path_service.seed_defaults()


@router.post("/add-project-group")
def add_project_group(payload: ProjectGroupRequest) -> dict[str, Any]:
    return real_work_fast_path_service.add_project_group(
        label=payload.label,
        aliases=payload.aliases,
        expected_fronts=payload.expected_fronts,
        description=payload.description,
    )


@router.post("/link-repo")
def link_repo(payload: RepoLinkRequest) -> dict[str, Any]:
    return real_work_fast_path_service.link_repo(
        repo_full_name=payload.repo_full_name,
        project_hint=payload.project_hint,
        front=payload.front,
        evidence=payload.evidence,
    )


@router.post("/link-conversation")
def link_conversation(payload: ConversationLinkRequest) -> dict[str, Any]:
    return real_work_fast_path_service.link_conversation(
        title=payload.title,
        provider=payload.provider,
        project_hint=payload.project_hint,
        source_ref=payload.source_ref,
        summary=payload.summary,
    )


@router.post("/classify-text")
def classify_text(payload: ClassifyTextRequest) -> dict[str, Any]:
    return real_work_fast_path_service.classify_text(payload.text)


@router.post("/create-work-run")
def create_work_run(payload: WorkRunRequest) -> dict[str, Any]:
    return real_work_fast_path_service.create_work_run(
        operator_request=payload.operator_request,
        project_hint=payload.project_hint,
        selected_provider_ids=payload.selected_provider_ids,
    )


@router.get("/first-pc-fast-path")
@router.post("/first-pc-fast-path")
def first_pc_fast_path() -> dict[str, Any]:
    return real_work_fast_path_service.first_pc_fast_path()


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return real_work_fast_path_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return real_work_fast_path_service.package()
