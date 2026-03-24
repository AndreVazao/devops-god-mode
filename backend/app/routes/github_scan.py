from fastapi import APIRouter, HTTPException

from app.services.github_service import github_service

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/status")
async def github_status():
    return {"configured": github_service.is_configured()}


@router.get("/scan")
async def github_scan(limit: int = 10):
    if not github_service.is_configured():
        raise HTTPException(status_code=400, detail="github_not_configured")
    return await github_service.scan_repositories(limit=limit)
