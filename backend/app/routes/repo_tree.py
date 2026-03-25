from fastapi import APIRouter

router = APIRouter(prefix="/repo/tree", tags=["repo-tree"])

@router.get("/status")
async def repo_tree_status():
    return {"ok": True}
