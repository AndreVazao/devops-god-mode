from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/api/system/config")
def config_status():
    return {
        "supabase": bool(settings.SUPABASE_URL),
        "github": bool(settings.GITHUB_TOKEN),
        "vercel": bool(settings.VERCEL_TOKEN),
        "openai": bool(settings.OPENAI_KEY),
    }
