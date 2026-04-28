from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.install_first_run_guide_service import install_first_run_guide_service
from app.services.install_readiness_final_service import install_readiness_final_service


class FirstRealInstallLauncherService:
    """Operator-facing final launcher for the first real PC/APK install."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_plan(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        readiness = install_readiness_final_service.build_check(
            tenant_id=tenant_id,
            requested_project=requested_project,
            run_deep=False,
        )
        guide = install_first_run_guide_service.build_guide(tenant_id=tenant_id)
        artifacts = artifacts_center_service.build_dashboard()
        artifact_map = {item["id"]: item for item in artifacts.get("artifacts", [])}
        blockers = self._blockers(readiness=readiness, guide=guide, artifacts=artifacts)
        status = "ready_to_launch" if not blockers else "blocked"
        return {
            "ok": status == "ready_to_launch",
            "mode": "first_real_install_launcher",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": status,
            "ready_to_launch": not blockers,
            "blockers": blockers,
            "primary_button": {
                "label": "Abrir centro APK/EXE",
                "endpoint": "/api/artifacts-center/dashboard",
                "route": "/app/home",
                "enabled": not blockers,
            },
            "install_cards": [
                {
                    "id": "pc_exe",
                    "title": "1. PC: abrir GodModeDesktop.exe",
                    "artifact": "godmode-windows-exe",
                    "expected_file": artifact_map.get("exe", {}).get("expected_file", "GodModeDesktop.exe"),
                    "target": "PC Windows",
                    "instruction": "Descarrega o artifact do workflow Windows EXE Build, extrai se necessário, abre GodModeDesktop.exe e confirma que /health responde.",
                    "success_signal": "Home abre no PC e mostra semáforo/próxima tarefa.",
                },
                {
                    "id": "apk",
                    "title": "2. Telemóvel: instalar GodModeMobile-debug.apk",
                    "artifact": "godmode-android-webview-apk",
                    "expected_file": artifact_map.get("apk", {}).get("expected_file", "GodModeMobile-debug.apk"),
                    "target": "Android",
                    "instruction": "Instala o APK, aponta para o URL do backend no PC e entra em /app/home.",
                    "success_signal": "APK controla a Home do backend no PC.",
                },
                {
                    "id": "first_command",
                    "title": "3. Primeira ordem real",
                    "artifact": None,
                    "expected_file": None,
                    "target": "Home / Modo Fácil",
                    "instruction": "Carrega em Instalação final, depois Teste geral, e só então envia a primeira ordem real.",
                    "success_signal": "Backend cria job e só para por fim, OK, intervenção manual ou bloqueio seguro.",
                },
            ],
            "download_targets": [
                {
                    "label": "GodModeDesktop.exe",
                    "artifact_name": "godmode-windows-exe",
                    "workflow": ".github/workflows/windows-exe-real-build.yml",
                },
                {
                    "label": "GodModeMobile-debug.apk",
                    "artifact_name": "godmode-android-webview-apk",
                    "workflow": ".github/workflows/android-real-build-progressive.yml",
                },
            ],
            "home_actions": [
                {"label": "Instalação final", "endpoint": "/api/install-readiness-final/check"},
                {"label": "Guia 1º arranque", "endpoint": "/api/install-first-run/guide"},
                {"label": "APK/EXE", "endpoint": "/api/artifacts-center/dashboard"},
                {"label": "Home", "route": "/app/home"},
            ],
            "safety": {
                "no_destructive_actions": True,
                "preserve_local_state": ["data/", "memory/", ".env", "backend/.env"],
                "operator_priority_source": "operator",
                "backend_stop_contract": ["finished", "operator_ok_required", "manual_action_required", "safe_blocked"],
            },
            "signals": {
                "readiness_status": readiness.get("status"),
                "readiness_score": readiness.get("score"),
                "install_status": guide.get("status"),
                "install_done_count": guide.get("done_count"),
                "artifact_count": artifacts.get("artifact_count"),
            },
        }

    def _blockers(self, readiness: Dict[str, Any], guide: Dict[str, Any], artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        blockers: List[Dict[str, Any]] = []
        if readiness.get("ready_to_install") is not True:
            blockers.append({"id": "install_readiness", "label": "Instalação final ainda não está ready", "detail": readiness.get("failed_checks", [])[:3]})
        if artifacts.get("status") != "ready" or artifacts.get("artifact_count") != 2:
            blockers.append({"id": "artifacts", "label": "Artifacts APK/EXE ainda não estão prontos", "detail": artifacts.get("missing_required_workflows", [])})
        expected = {item.get("expected_file") for item in artifacts.get("artifacts", [])}
        for required in ["GodModeDesktop.exe", "GodModeMobile-debug.apk"]:
            if required not in expected:
                blockers.append({"id": f"missing_{required}", "label": f"Falta artifact esperado {required}", "detail": sorted(expected)})
        if guide.get("blocked_count", 0) > 0 and guide.get("done_count", 0) == 0:
            blockers.append({"id": "guide", "label": "Guia de primeiro arranque não tem passos desbloqueados", "detail": guide.get("current_step")})
        return blockers

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        plan = self.build_plan(tenant_id=tenant_id)
        return {
            "ok": plan["ok"],
            "mode": "first_real_install_launcher_status",
            "status": plan["status"],
            "ready_to_launch": plan["ready_to_launch"],
            "blocker_count": len(plan["blockers"]),
            "primary_button": plan["primary_button"],
            "signals": plan["signals"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "first_real_install_launcher_package",
            "package": {
                "status": self.get_status(tenant_id=tenant_id),
                "plan": self.build_plan(tenant_id=tenant_id, requested_project=requested_project),
            },
        }


first_real_install_launcher_service = FirstRealInstallLauncherService()
