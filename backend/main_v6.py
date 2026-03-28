from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.github_scan import router as github_scan_router
from app.routes.registry import router as registry_router
from app.routes.repo_tree_v6 import router as repo_tree_router

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
app.include_router(repo_tree_router)


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
