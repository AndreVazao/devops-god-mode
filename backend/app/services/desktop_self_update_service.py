from __future__ import annotations

import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CURRENT_VERSION = "0.150.0"
CURRENT_PHASE = "phase150-desktop-self-updater-bootstrap"
APP_NAME = "GodModeDesktop"
DEFAULT_CHANNEL = "stable"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DesktopSelfUpdateService:
    def appdata_dir(self) -> Path:
        base = os.environ.get("APPDATA")
        if not base:
            base = str(Path.home() / "AppData" / "Roaming")
        target = Path(base) / APP_NAME
        target.mkdir(parents=True, exist_ok=True)
        return target

    def runtime_state_path(self) -> Path:
        return self.appdata_dir() / "desktop_runtime_state.json"

    def local_update_manifest_path(self) -> Path:
        return self.appdata_dir() / "desktop_update_manifest.json"

    def pending_update_path(self) -> Path:
        return self.appdata_dir() / "desktop_pending_update.json"

    def update_log_path(self) -> Path:
        return self.appdata_dir() / "desktop_update.log"

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def status(self) -> dict[str, Any]:
        state = self._read_json(self.runtime_state_path())
        local_manifest = self._read_json(self.local_update_manifest_path())
        pending = self._read_json(self.pending_update_path())
        return {
            "ok": True,
            "service": "desktop_self_update",
            "app_name": APP_NAME,
            "current_version": CURRENT_VERSION,
            "current_phase": CURRENT_PHASE,
            "channel": DEFAULT_CHANNEL,
            "platform": platform.platform(),
            "runtime_state": state,
            "local_update_manifest": local_manifest,
            "pending_update": pending,
            "paths": {
                "appdata_dir": str(self.appdata_dir()),
                "runtime_state": str(self.runtime_state_path()),
                "local_update_manifest": str(self.local_update_manifest_path()),
                "pending_update": str(self.pending_update_path()),
                "update_log": str(self.update_log_path()),
            },
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Desktop Self Updater",
            "description": "Base para o God Mode atualizar EXE/backend por pacote, sem reinstalação completa.",
            "primary_actions": [
                {
                    "label": "Ver estado de update",
                    "endpoint": "/api/desktop-self-update/status",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Ver manifesto local",
                    "endpoint": "/api/desktop-self-update/manifest",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Ver política de atualização",
                    "endpoint": "/api/desktop-self-update/policy",
                    "method": "GET",
                    "safe": True,
                },
            ],
        }

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "rules": [
                "A versão antiga sem updater precisa de uma instalação manual inicial.",
                "Depois do updater existir no EXE, atualizações futuras podem ser aplicadas por pacote.",
                "Dados do operador ficam fora da pasta do EXE, em APPDATA, para sobreviverem a updates.",
                "O update deve fazer backup do EXE anterior antes de substituir.",
                "Se a atualização falhar, o God Mode deve manter rollback possível.",
                "Nunca apagar memória, logs, credenciais locais ou configurações durante update.",
                "Pacotes remotos privados podem exigir token GitHub ou um canal próprio de distribuição.",
            ],
            "update_modes": {
                "manual_bootstrap": "obrigatório para instalar o primeiro EXE que já contém updater",
                "package_update": "substitui EXE/backend por ZIP assinado/verificado quando disponível",
                "artifact_update": "usa artifacts GitHub quando houver autenticação configurada",
                "local_package_update": "aplica pacote transferido manualmente ou pelo telemóvel/Drive/túnel",
            },
            "preserve_paths": [
                "%APPDATA%/GodModeDesktop",
                "AndreOS local vault",
                "repo AndreVazao/andreos-memory",
                "data local importante",
            ],
        }

    def manifest(self) -> dict[str, Any]:
        payload = {
            "ok": True,
            "app_name": APP_NAME,
            "version": CURRENT_VERSION,
            "phase": CURRENT_PHASE,
            "channel": DEFAULT_CHANNEL,
            "generated_at": _utc_now(),
            "backend_port": 8000,
            "health_path": "/health",
            "home_path": "/app/home",
            "update_capabilities": {
                "self_update_bootstrap": True,
                "package_update": True,
                "rollback_backup": True,
                "preserve_appdata": True,
                "remote_artifact_requires_auth": True,
            },
            "notes": [
                "Este manifesto declara a versão instalada e capacidades de update.",
                "O primeiro EXE com updater ainda tem de ser instalado manualmente.",
                "Depois, updates podem ser preparados e aplicados por pacote.",
            ],
        }
        self._write_json(self.local_update_manifest_path(), payload)
        return payload

    def compare(self, latest_version: str | None = None, latest_phase: str | None = None) -> dict[str, Any]:
        latest_version = latest_version or CURRENT_VERSION
        latest_phase = latest_phase or CURRENT_PHASE
        update_available = latest_version != CURRENT_VERSION or latest_phase != CURRENT_PHASE
        return {
            "ok": True,
            "current_version": CURRENT_VERSION,
            "current_phase": CURRENT_PHASE,
            "latest_version": latest_version,
            "latest_phase": latest_phase,
            "update_available": update_available,
            "recommended_action": "prepare_package_update" if update_available else "already_current",
        }

    def prepare_local_package_update(
        self,
        package_path: str,
        target_version: str,
        target_phase: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        path = Path(package_path).expanduser()
        if not path.exists():
            return {
                "ok": False,
                "error_type": "package_not_found",
                "package_path": str(path),
            }
        payload = {
            "ok": True,
            "created_at": _utc_now(),
            "package_path": str(path),
            "target_version": target_version,
            "target_phase": target_phase,
            "current_version": CURRENT_VERSION,
            "current_phase": CURRENT_PHASE,
            "notes": notes,
            "status": "pending_operator_restart_or_apply",
            "apply_helper": "desktop/godmode_update_helper.py",
        }
        self._write_json(self.pending_update_path(), payload)
        return payload

    def clear_pending_update(self) -> dict[str, Any]:
        path = self.pending_update_path()
        if path.exists():
            path.unlink()
        return {"ok": True, "status": "pending_update_cleared"}

    async def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "policy": self.policy(),
            "manifest": self.manifest(),
        }


desktop_self_update_service = DesktopSelfUpdateService()
