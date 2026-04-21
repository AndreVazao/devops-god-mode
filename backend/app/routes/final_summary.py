from fastapi import APIRouter, HTTPException

from app.services.final_summary_service import final_summary_service

router = APIRouter(
    prefix="/api/final-summary",
    tags=["final-summary"],
)


@router.get("/status")
async def final_summary_status():
    summaries = final_summary_service.get_summaries()["summaries"]
    return {
        "ok": True,
        "mode": "final_summary_status",
        "summaries_count": len(summaries),
        "summary_status": "final_summary_ready",
    }


@router.get("/summaries")
async def final_summaries():
    return final_summary_service.get_summaries()


@router.get("/lines")
async def final_summary_lines(recovery_project_id: str | None = None):
    return final_summary_service.get_summary_lines(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def final_summary_package(recovery_project_id: str):
    try:
        return final_summary_service.get_summary_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-summary-action")
async def final_summary_next_action():
    return final_summary_service.get_next_summary_action()
