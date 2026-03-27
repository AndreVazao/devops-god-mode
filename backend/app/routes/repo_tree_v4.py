from fastapi import APIRouter, HTTPException

from app.services.repo_tree_engine_v3 import repo_tree_engine_v3

router = APIRouter(prefix="/repo/tree", tags=["repo-tree"])


@router.get("/status")
async def repo_tree_status():
    return repo_tree_engine_v3.status()


@router.get("/preview")
async def repo_tree_preview(repo_full_name: str, depth: int = 2):
    if depth < 1:
        raise HTTPException(status_code=400, detail="depth_must_be_positive")
    try:
        return await repo_tree_engine_v3.preview(repo_full_name, depth=depth)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_preview_failed",
            "message": "A geração da árvore falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
            "depth": depth,
        }
