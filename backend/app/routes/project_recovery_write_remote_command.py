from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_remote_command_service import (
    project_recovery_write_remote_command_service,
)

router = APIRouter(
    prefix="/api/project-recovery-write-remote-command",
    tags=["project-recovery-write-remote-command"],
)


@router.get("/status")
async def project_recovery_write_remote_command_status():
    commands = project_recovery_write_remote_command_service.get_remote_commands()["commands"]
    return {
        "ok": True,
        "mode": "project_recovery_write_remote_command_status",
        "commands_count": len(commands),
        "remote_status": "project_recovery_write_remote_command_ready",
    }


@router.get("/commands")
async def project_recovery_write_remote_commands():
    return project_recovery_write_remote_command_service.get_remote_commands()


@router.get("/actions")
async def project_recovery_write_remote_actions(recovery_project_id: str | None = None):
    return project_recovery_write_remote_command_service.get_remote_actions(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_remote_command_package(recovery_project_id: str):
    try:
        return project_recovery_write_remote_command_service.get_remote_command_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-remote-action")
async def project_recovery_write_next_remote_action():
    return project_recovery_write_remote_command_service.get_next_remote_action()
