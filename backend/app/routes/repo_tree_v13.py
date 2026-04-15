from fastapi import APIRouter, HTTPException

from app.services.repo_tree_action_plan_v2 import repo_tree_action_plan_v2
from app.services.repo_tree_action_plan_v3 import repo_tree_action_plan_v3
from app.services.repo_tree_advice_v1 import repo_tree_advice_v1
from app.services.repo_tree_cockpit_v1 import repo_tree_cockpit_v1
from app.services.repo_tree_drift_v1 import repo_tree_drift_v1
from app.services.repo_tree_engine_v4 import repo_tree_engine_v4
from app.services.repo_tree_snapshot_reader_v1 import repo_tree_snapshot_reader_v1

router = APIRouter(prefix="/repo/tree", tags=["repo-tree"])


@router.get("/status")
async def repo_tree_status():
    return repo_tree_engine_v4.status()


@router.get("/preview")
async def repo_tree_preview(repo_full_name: str, depth: int = 2):
    if depth < 1:
        raise HTTPException(status_code=400, detail="depth_must_be_positive")
    try:
        return await repo_tree_engine_v4.preview(repo_full_name, depth=depth)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_preview_failed",
            "message": "A geração da árvore falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
            "depth": depth,
        }


@router.get("/latest")
async def repo_tree_latest(repo_full_name: str):
    try:
        return await repo_tree_snapshot_reader_v1.latest_snapshot(repo_full_name)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_latest_failed",
            "message": "A leitura do snapshot mais recente falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
        }


@router.get("/advice")
async def repo_tree_advice(repo_full_name: str):
    try:
        latest = await repo_tree_snapshot_reader_v1.latest_snapshot(repo_full_name)
        if not latest.get("ok"):
            return latest
        return repo_tree_advice_v1.build(latest)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_advice_failed",
            "message": "A geração de conselho operacional falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
        }


@router.get("/cockpit")
async def repo_tree_cockpit(repo_full_name: str):
    try:
        latest = await repo_tree_snapshot_reader_v1.latest_snapshot(repo_full_name)
        if not latest.get("ok"):
            return latest
        return repo_tree_cockpit_v1.build(latest)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_cockpit_failed",
            "message": "A geração do cockpit estrutural falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
        }


@router.get("/drift")
async def repo_tree_drift(repo_full_name: str):
    try:
        latest = await repo_tree_snapshot_reader_v1.latest_snapshot(repo_full_name)
        if not latest.get("ok"):
            return latest
        return repo_tree_drift_v1.compare(latest)
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_drift_failed",
            "message": "A geração da avaliação de drift falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
        }


@router.get("/action-plan")
async def repo_tree_action_plan(repo_full_name: str):
    latest = None
    latest_error = None
    try:
        latest = await repo_tree_snapshot_reader_v1.latest_snapshot(repo_full_name)
    except Exception as exc:
        latest_error = str(exc)

    try:
        if latest and latest.get("ok"):
            return repo_tree_action_plan_v2.build_from_snapshot(latest)

        live = await repo_tree_action_plan_v3.build_live(repo_full_name, depth=2)
        if latest_error:
            live["latest_snapshot_error"] = latest_error
        elif latest and not latest.get("ok"):
            live["latest_snapshot_error"] = latest.get("reason", "latest_snapshot_unavailable")
        return live
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "repo_tree_action_plan_failed",
            "message": "A geração do plano de ação falhou.",
            "technical_error": str(exc),
            "repo_full_name": repo_full_name,
            "latest_snapshot_error": latest_error,
        }
