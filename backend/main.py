from fastapi import FastAPI
from app.config import settings
from app.routes.github_scan import router as github_scan_router

app = FastAPI(title="DevOps God Mode")

app.include_router(github_scan_router)

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
