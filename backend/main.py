from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.approval_broker import router as approval_broker_router
from app.routes.approval_gated_execution import router as approval_gated_execution_router
from app.routes.browser_conversation_intake import router as browser_conversation_intake_router
from app.routes.conversation_repo_reconstruction import (
    router as conversation_repo_reconstruction_router,
)
from app.routes.github_scan import router as github_scan_router
from app.routes.local_code_patch import router as local_code_patch_router
from app.routes.local_file_apply_runtime import router as local_file_apply_runtime_router
from app.routes.local_real_validator import router as local_real_validator_router
from app.routes.packaging_foundation import router as packaging_foundation_router
from app.routes.patch_apply_preview import router as patch_apply_preview_router
from app.routes.real_local_write import router as real_local_write_router
from app.routes.registry import router as registry_router
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
