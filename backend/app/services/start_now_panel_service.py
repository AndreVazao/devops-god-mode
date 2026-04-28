from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_real_install_launcher_service import first_real_install_launcher_service
from app.services.home_command_wizard_service import home_command_wizard_service
from app.services.install_readiness_final_service import install_readiness_final_service
from app.services.pc_link_helper_service import pc_link_helper_service


class StartNowPanelService:
    """One mobile-first panel for the real operator starting flow."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_panel(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        pc_link = pc_link_helper_service.build_panel()
        launch = first_real_install_launcher_service.build_plan(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        readiness = install_readiness_final_service.build_check(
            tenant_id=tenant_id,
            requested_project=requested_project,
            run_deep=False,
        )
        artifacts = artifacts_center_service.build_dashboard()
        wizard = home_command_wizard_service.build_panel(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        blockers = self._blockers(readiness=readiness, launch=launch, artifacts=artifacts)
        status = "ready" if not blockers else "attention"
        return {
            "ok": not blockers,
            "mode": "start_now_panel",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "headline": "Começar agora",
            "status": status,
            "blockers": blockers,
            "primary_action": self._primary_action(blockers=blockers, wizard=wizard),
            "cards": [
                {
                    "id": "pc_link",
                    "title": "1. Ligar telemóvel ao PC",
                    "endpoint": "/api/pc-link-helper/panel",
                    "status": pc_link.get("status"),
                    "summary": pc_link.get("primary_url"),
                },
                {
                    "id": "install_ready",
                    "title": "2. Confirmar instalação final",
                    "endpoint": "/api/install-readiness-final/check",
                    "status": readiness.get("status"),
                    "summary": f"score {readiness.get('score')}%",
                },
                {
                    "id": "artifacts",
                    "title": "3. APK/EXE",
                    "endpoint": "/api/artifacts-center/dashboard",
                    "status": artifacts.get("status"),
                    "summary": f"{artifacts.get('artifact_count')} artifacts esperados",
                },
                {
                    "id": "next_command",
                    "title": "4. Próxima ordem",
                    "endpoint": "/api/home-command-wizard/panel",
                    "status": wizard.get("status"),
                    "summary": wizard.get("primary_command", {}).get("label"),
                },
            ],
            "quick_buttons": [
                {"label": "Ligar ao PC", "endpoint": "/api/pc-link-helper/panel"},
                {"label": "Instalação final", "endpoint": "/api/install-readiness-final/check"},
                {"label": "APK/EXE", "endpoint": "/api/artifacts-center/dashboard"},
                {"label": "Próxima ordem", "endpoint": "/api/home-command-wizard/panel"},
                {"label": "Home", "route": "/app/home"},
            ],
            "signals": {
                "pc_candidate_count": len(pc_link.get("candidate_urls", [])),
                "launch_ready": launch.get("ready_to_launch"),
                "install_ready": readiness.get("ready_to_install"),
                "install_score": readiness.get("score"),
                "artifact_count": artifacts.get("artifact_count"),
                "wizard_command_count": len(wizard.get("commands", [])),
            },
        }

    def _blockers(self, readiness: Dict[str, Any], launch: Dict[str, Any], artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        blockers: List[Dict[str, Any]] = []
        if readiness.get("ready_to_install") is not True:
            blockers.append({"id": "install_readiness", "label": "Instalação final ainda precisa atenção", "endpoint": "/api/install-readiness-final/check"})
        if launch.get("ready_to_launch") is not True:
            blockers.append({"id": "launch", "label": "Plano de arranque ainda precisa atenção", "endpoint": "/api/first-real-install-launcher/plan"})
        if artifacts.get("status") != "ready" or artifacts.get("artifact_count") != 2:
            blockers.append({"id": "artifacts", "label": "APK/EXE ainda não estão prontos", "endpoint": "/api/artifacts-center/dashboard"})
        return blockers

    def _primary_action(self, blockers: List[Dict[str, Any]], wizard: Dict[str, Any]) -> Dict[str, Any]:
        if blockers:
            first = blockers[0]
            return {"label": first["label"], "endpoint": first["endpoint"], "enabled": True}
        return {
            "label": wizard.get("primary_command", {}).get("button_text", "Próxima ordem"),
            "endpoint": "/api/home-command-wizard/panel",
            "enabled": True,
        }

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        panel = self.build_panel(tenant_id=tenant_id)
        return {
            "ok": panel["ok"],
            "mode": "start_now_panel_status",
            "status": panel["status"],
            "blocker_count": len(panel["blockers"]),
            "primary_action": panel["primary_action"],
            "signals": panel["signals"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "start_now_panel_package",
            "package": {
                "status": self.get_status(tenant_id=tenant_id),
                "panel": self.build_panel(tenant_id=tenant_id, requested_project=requested_project),
            },
        }


start_now_panel_service = StartNowPanelService()
