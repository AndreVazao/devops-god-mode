from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.offline_command_buffering_service import offline_command_buffering_service

router = APIRouter(prefix="/api/offline-command-buffering", tags=["offline-command-buffering"])


class ConnectivityUpdateRequest(BaseModel):
    pc_online: bool
    phone_online: bool


class QueueOfflineCommandRequest(BaseModel):
    source_side: str
    command_text: str
    target_scope: str = "pc_primary_executor"
    autonomy_mode: str = "continue_until_blocked_or_finished"
    project_hint: str | None = None


class CommandExecutionUpdateRequest(BaseModel):
    execution_status: str
    requires_clarification: bool = False


class ReplayRequest(BaseModel):
    tenant_id: str = "owner-andre"
    auto_run: bool = True
    max_commands: int = 10


@router.get("/status")
async def offline_command_buffering_status():
    buffers = offline_command_buffering_service.get_buffers()["buffers"]
    connectivity = offline_command_buffering_service.get_connectivity()["connectivity"]
    package = offline_command_buffering_service.get_buffer_package()["package"]
    return {
        "ok": True,
        "mode": "offline_command_buffering_status",
        "buffers_count": len(buffers),
        "buffer_status": "offline_command_buffering_ready",
        "link_mode": connectivity["link_mode"],
        "atomic_store_enabled": package.get("atomic_store_enabled", False),
        "request_orchestrator_bridge": package.get("request_orchestrator_bridge", False),
    }


@router.get("/connectivity")
async def offline_command_connectivity():
    return offline_command_buffering_service.get_connectivity()


@router.post("/connectivity")
async def update_offline_command_connectivity(payload: ConnectivityUpdateRequest):
    return offline_command_buffering_service.set_connectivity(pc_online=payload.pc_online, phone_online=payload.phone_online)


@router.get("/buffers")
async def offline_command_buffers():
    return offline_command_buffering_service.get_buffers()


@router.get("/commands")
async def offline_command_queue(sync_status: str | None = None):
    return offline_command_buffering_service.get_commands(sync_status=sync_status)


@router.post("/commands")
async def queue_offline_command(payload: QueueOfflineCommandRequest):
    try:
        return offline_command_buffering_service.queue_command(
            source_side=payload.source_side,
            command_text=payload.command_text,
            target_scope=payload.target_scope,
            autonomy_mode=payload.autonomy_mode,
            project_hint=payload.project_hint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sync")
async def sync_offline_commands_to_pc():
    return offline_command_buffering_service.sync_buffered_commands_to_pc()


@router.post("/replay")
async def replay_ready_commands(payload: ReplayRequest):
    return offline_command_buffering_service.replay_ready_commands_to_orchestrator(
        tenant_id=payload.tenant_id,
        auto_run=payload.auto_run,
        max_commands=payload.max_commands,
    )


@router.post("/sync-and-replay")
async def sync_and_replay(payload: ReplayRequest):
    return offline_command_buffering_service.sync_and_replay_to_pc(
        tenant_id=payload.tenant_id,
        auto_run=payload.auto_run,
        max_commands=payload.max_commands,
    )


@router.get("/replays")
async def offline_replays(limit: int = 50):
    return offline_command_buffering_service.get_replays(limit=limit)


@router.post("/commands/{command_id}/execution")
async def mark_offline_command_execution(command_id: str, payload: CommandExecutionUpdateRequest):
    try:
        return offline_command_buffering_service.mark_command_execution(
            command_id=command_id,
            execution_status=payload.execution_status,
            requires_clarification=payload.requires_clarification,
        )
    except ValueError as exc:
        detail = str(exc)
        if detail == "command_not_found":
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)


@router.get("/actions")
async def offline_buffer_actions(buffer_area: str | None = None):
    return offline_command_buffering_service.get_buffer_actions(buffer_area)


@router.get("/package")
async def offline_buffer_package():
    return offline_command_buffering_service.get_buffer_package()


@router.get("/next-buffer-action")
async def next_offline_buffer_action():
    return offline_command_buffering_service.get_next_buffer_action()
