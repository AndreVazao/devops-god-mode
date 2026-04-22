from fastapi import APIRouter

from app.services.continuous_remote_execution_service import (
    continuous_remote_execution_service,
)

router = APIRouter(
    prefix="/api/continuous-remote-execution",
    tags=["continuous-remote-execution"],
)


@router.get("/status")
async def continuous_remote_execution_status():
    loops = continuous_remote_execution_service.get_execution_loops()["loops"]
    next_action = continuous_remote_execution_service.get_next_execution_action()[
        "next_execution_action"
    ]
    package = continuous_remote_execution_service.get_execution_package()["package"]
    return {
        "ok": True,
        "mode": "continuous_remote_execution_status",
        "loops_count": len(loops),
        "execution_status": "pc_autonomy_loop_ready",
        "next_execution_action_id": next_action["continuous_execution_action_id"]
        if next_action
        else None,
        "counts": package["counts"],
        "link_mode": package["connectivity"]["link_mode"],
    }


@router.get("/loops")
async def continuous_remote_execution_loops():
    return continuous_remote_execution_service.get_execution_loops()


@router.get("/actions")
async def continuous_remote_execution_actions(execution_area: str | None = None):
    return continuous_remote_execution_service.get_execution_actions(execution_area)


@router.get("/package")
async def continuous_remote_execution_package():
    return continuous_remote_execution_service.get_execution_package()


@router.get("/next-execution-action")
async def next_continuous_remote_execution_action():
    return continuous_remote_execution_service.get_next_execution_action()
