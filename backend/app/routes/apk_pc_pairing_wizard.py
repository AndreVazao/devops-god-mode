from fastapi import APIRouter
from pydantic import BaseModel

from app.services.apk_pc_pairing_wizard_service import apk_pc_pairing_wizard_service

router = APIRouter(prefix="/api/apk-pc-pairing", tags=["apk-pc-pairing"])


class PairingStartRequest(BaseModel):
    port: int = 8000
    label: str = "God Mode PC"


class PairingConfirmRequest(BaseModel):
    session_id: str
    pairing_code: str
    token: str
    apk_device_label: str = "Android APK"


class PairingHeartbeatRequest(BaseModel):
    session_id: str
    apk_device_label: str = "Android APK"


@router.get('/status')
async def status():
    return apk_pc_pairing_wizard_service.get_status()


@router.post('/status')
async def post_status():
    return apk_pc_pairing_wizard_service.get_status()


@router.get('/panel')
async def panel():
    return apk_pc_pairing_wizard_service.panel()


@router.post('/panel')
async def post_panel():
    return apk_pc_pairing_wizard_service.panel()


@router.get('/guide')
async def guide():
    return apk_pc_pairing_wizard_service.guide()


@router.post('/guide')
async def post_guide():
    return apk_pc_pairing_wizard_service.guide()


@router.post('/start')
async def start(payload: PairingStartRequest):
    return apk_pc_pairing_wizard_service.start(port=payload.port, label=payload.label)


@router.post('/confirm')
async def confirm(payload: PairingConfirmRequest):
    return apk_pc_pairing_wizard_service.confirm(
        session_id=payload.session_id,
        pairing_code=payload.pairing_code,
        token=payload.token,
        apk_device_label=payload.apk_device_label,
    )


@router.post('/heartbeat')
async def heartbeat(payload: PairingHeartbeatRequest):
    return apk_pc_pairing_wizard_service.heartbeat(
        session_id=payload.session_id,
        apk_device_label=payload.apk_device_label,
    )


@router.get('/latest')
async def latest():
    return apk_pc_pairing_wizard_service.latest()


@router.post('/latest')
async def post_latest():
    return apk_pc_pairing_wizard_service.latest()


@router.get('/package')
async def package():
    return apk_pc_pairing_wizard_service.get_package()


@router.post('/package')
async def post_package():
    return apk_pc_pairing_wizard_service.get_package()
