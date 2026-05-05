from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_prompt_broadcast_runtime_service import provider_prompt_broadcast_runtime_service

router = APIRouter(prefix="/api/provider-prompt-broadcast-runtime", tags=["provider-prompt-broadcast-runtime"])


class PaneProfileProvider(BaseModel):
    provider_id: str
    label: str | None = None
    kind: str | None = None
    enabled: bool = True
    pane_order: int | None = None
    ledger_role: str | None = None
    requires_login_attention: bool = False


class CreatePaneProfileRequest(BaseModel):
    profile_name: str = "custom_multi_ai_cockpit"
    providers: list[dict[str, Any]]
    layout: dict[str, Any] | None = None


class CreateBroadcastPlanRequest(BaseModel):
    operator_request: str
    project_key: str = "GOD_MODE"
    selected_provider_ids: list[str] | None = None
    profile_id: str | None = None
    context_bundle_ref: str | None = None
    prompt_mode: str = "plain"
    use_prompt_critic: bool = False


class ImportProviderResponseRequest(BaseModel):
    plan_id: str
    provider_id: str
    response_text: str
    source_mode: str = "manual_import"


class CompareResponsesRequest(BaseModel):
    plan_id: str


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.policy()


@router.post("/default-pane-profile")
def default_pane_profile(profile_name: str = "default_multi_ai_cockpit") -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.default_pane_profile(profile_name=profile_name)


@router.post("/create-pane-profile")
def create_pane_profile(payload: CreatePaneProfileRequest) -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.create_pane_profile(
        profile_name=payload.profile_name,
        providers=payload.providers,
        layout=payload.layout,
    )


@router.post("/create-broadcast-plan")
def create_broadcast_plan(payload: CreateBroadcastPlanRequest) -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.create_broadcast_plan(
        operator_request=payload.operator_request,
        project_key=payload.project_key,
        selected_provider_ids=payload.selected_provider_ids,
        profile_id=payload.profile_id,
        context_bundle_ref=payload.context_bundle_ref,
        prompt_mode=payload.prompt_mode,
        use_prompt_critic=payload.use_prompt_critic,
    )


@router.post("/import-provider-response")
def import_provider_response(payload: ImportProviderResponseRequest) -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.import_provider_response(
        plan_id=payload.plan_id,
        provider_id=payload.provider_id,
        response_text=payload.response_text,
        source_mode=payload.source_mode,
    )


@router.post("/compare-responses")
def compare_responses(payload: CompareResponsesRequest) -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.compare_responses(plan_id=payload.plan_id)


@router.get("/plans")
@router.post("/plans")
def plans(limit: int = 50) -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.list_plans(limit=limit)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return provider_prompt_broadcast_runtime_service.package()
