from fastapi import APIRouter, HTTPException

from app.services.registry_service import registry_service

router = APIRouter(prefix="/registry", tags=["registry"])


@router.get("/status")
async def registry_status():
    return {"configured": registry_service.is_configured()}


@router.get("/github-preview")
async def registry_github_preview(limit: int = 10):
    if not registry_service.is_configured():
        raise HTTPException(status_code=400, detail="supabase_not_configured")

    try:
        return await registry_service.build_preview(limit=limit)
    except Exception as exc:
        return {
            "ok": False,
            "mode": "preview",
            "error_type": "registry_preview_failed",
            "message": "O preview do registry falhou antes de devolver resultados.",
            "technical_error": str(exc),
            "limit": limit,
            "ecosystems": [],
            "relations": [],
            "risks": [],
            "repositories": [],
            "unclassified_repos": [],
        }


@router.post("/github-ingest")
async def registry_github_ingest(limit: int = 10):
    if not registry_service.is_configured():
        raise HTTPException(status_code=400, detail="supabase_not_configured")

    try:
        return await registry_service.ingest_preview(limit=limit)
    except Exception as exc:
        return {
            "ok": False,
            "mode": "ingest",
            "error_type": "registry_ingest_failed",
            "message": "A gravação do registry falhou.",
            "technical_error": str(exc),
            "limit": limit,
        }
