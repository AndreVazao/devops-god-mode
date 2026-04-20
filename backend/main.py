from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.action_center import router as action_center_router
from app.routes.adaptation_planner import router as adaptation_planner_router
from app.routes.android_progressive_runtime_binding import (
    router as android_progressive_binding_router,
)
from app.routes.android_real_build_pipeline import router as android_real_build_router
from app.routes.android_real_build_progressive import router as android_real_build_progressive_router
from app.routes.android_real_pipeline_readiness import (
    router as android_real_pipeline_router,
)
from app.routes.approval_broker import router as approval_broker_router
from app.routes.approval_gated_execution import router as approval_gated_execution_router
from app.routes.browser_control_real import router as browser_control_real_router
from app.routes.browser_conversation_intake import router as browser_conversation_intake_router
from app.routes.chat_adapter_inventory import router as chat_inventory_router
from app.routes.context_aware_orchestration import router as context_orchestration_router
from app.routes.conversation_organization import router as conversation_organization_router
from app.routes.conversation_repo_reconstruction import (
    router as conversation_repo_reconstruction_router,
)
from app.routes.desktop_bootstrap import router as desktop_bootstrap_router
from app.routes.desktop_installer_onboarding import router as desktop_installer_router
from app.routes.desktop_mobile_handoff import router as desktop_mobile_handoff_router
from app.routes.driving_mode_voice_first import router as driving_mode_router
from app.routes.first_run_bundle import router as first_run_bundle_router
from app.routes.github_scan import router as github_scan_router
from app.routes.local_code_patch import router as local_code_patch_router
from app.routes.local_file_apply_runtime import router as local_file_apply_runtime_router
from app.routes.local_pc_runtime_orchestrator import router as local_pc_runtime_router
from app.routes.local_real_validator import router as local_real_validator_router
from app.routes.mobile_cockpit_command_surface import router as mobile_cockpit_router
from app.routes.mobile_runtime_shell import router as mobile_runtime_shell_router
from app.routes.operation_queue import router as operation_queue_router
from app.routes.packaging_foundation import router as packaging_foundation_router
from app.routes.patch_apply_preview import router as patch_apply_preview_router
from app.routes.pc_phone_bootstrap import router as pc_phone_bootstrap_router
from app.routes.real_local_write import router as real_local_write_router
from app.routes.registry import router as registry_router
from app.routes.runtime_supervisor_guidance import router as runtime_supervisor_router
from app.routes.script_extraction_reuse import router as script_reuse_router
from app.routes.write_verify_rollback import router as write_verify_rollback_router

app = FastAPI(title="DevOps God Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_scan_router)
app.include_router(registry_router)
app.include_router(approval_broker_router)
app.include_router(approval_gated_execution_router)
app.include_router(conversation_repo_reconstruction_router)
app.include_router(browser_conversation_intake_router)
app.include_router(local_code_patch_router)
app.include_router(patch_apply_preview_router)
app.include_router(local_file_apply_runtime_router)
app.include_router(real_local_write_router)
app.include_router(write_verify_rollback_router)
app.include_router(local_real_validator_router)
app.include_router(packaging_foundation_router)
app.include_router(pc_phone_bootstrap_router)
app.include_router(desktop_bootstrap_router)
app.include_router(first_run_bundle_router)
app.include_router(mobile_runtime_shell_router)
app.include_router(desktop_installer_router)
app.include_router(desktop_mobile_handoff_router)
app.include_router(runtime_supervisor_router)
app.include_router(local_pc_runtime_router)
app.include_router(action_center_router)
app.include_router(operation_queue_router)
app.include_router(chat_inventory_router)
app.include_router(script_reuse_router)
app.include_router(adaptation_planner_router)
app.include_router(conversation_organization_router)
app.include_router(browser_control_real_router)
app.include_router(mobile_cockpit_router)
app.include_router(driving_mode_router)
app.include_router(context_orchestration_router)
app.include_router(android_real_pipeline_router)
app.include_router(android_real_build_router)
app.include_router(android_real_build_progressive_router)
app.include_router(android_progressive_binding_router)


@app.get("/")
def root():
    return {"status": "DevOps God Mode backend alive"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/system/config")
def config_status():
    return {
        "supabase": bool(settings.SUPABASE_URL),
        "github": bool(settings.GITHUB_TOKEN),
        "vercel": bool(settings.VERCEL_TOKEN),
        "openai": bool(settings.OPENAI_KEY),
    }
