from fastapi import APIRouter
from pydantic import BaseModel

from app.services.project_tree_autorefresh_service import project_tree_autorefresh_service

router = APIRouter(prefix="/api/project-tree-autorefresh", tags=["project-tree-autorefresh"])


class WriteTreeRequest(BaseModel):
    allow_overwrite: bool = False


@router.get('/status')
async def status():
    return project_tree_autorefresh_service.get_status()


@router.get('/package')
async def package():
    return project_tree_autorefresh_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return project_tree_autorefresh_service.build_dashboard()


@router.get('/current')
async def current():
    return project_tree_autorefresh_service.read_current_tree()


@router.get('/generated')
async def generated():
    return {"ok": True, "mode": "project_tree_autorefresh_generated", "content": project_tree_autorefresh_service.build_tree_text()}


@router.get('/compare')
async def compare():
    return project_tree_autorefresh_service.compare_tree()


@router.post('/write')
async def write(payload: WriteTreeRequest):
    return project_tree_autorefresh_service.write_generated_tree(allow_overwrite=payload.allow_overwrite)
