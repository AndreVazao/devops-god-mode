from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List


class ReadyToUseHomeCheckService:
    """Operator-facing readiness check for actually using God Mode.

    This is not another cockpit to manage. It is a compact checklist for the
    Home screen: can the operator open the APK, land on Home, send a command,
    let the PC work, and approve blockers?
    """

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:240]}

    def _pc_autopilot(self):
        from app.services.pc_autopilot_loop_service import pc_autopilot_loop_service

        return pc_autopilot_loop_service

    def _operator_priority(self):
        from app.services.operator_priority_service import operator_priority_service

        return operator_priority_service

    def _chat_bridge(self):
        from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service

        return operator_chat_real_work_bridge_service

    def build_checklist(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        pc = self._safe("pc_autopilot", self._pc_autopilot().get_status)
        priority = self._safe("operator_priority", self._operator_priority().get_status)
        chat = self._safe("chat_bridge", self._chat_bridge().get_status)
        files = self._file_checks()
        checks = [
            self._check("home_route", "APK cai na Home principal", files["apk_home_entry"], "/app/home é a rota principal do APK"),
            self._check("home_backend_route", "Backend tem Home principal", files["home_backend_route_present"], "/app/home e /api/god-mode-home existem"),
            self._check("chat_pipeline", "Chat ligado ao trabalho real", chat.get("ok") is True, "/api/operator-chat-real-work/submit pronto"),
            self._check("operator_priority", "Prioridade do operador ativa", priority.get("ok") is True and priority.get("money_priority_enabled") is False, "ordem do operador vence dinheiro"),
            self._check("pc_autopilot", "PC Autopilot instalado", pc.get("ok") is True and pc.get("apk_disconnect_safe") is True, "PC consegue continuar com APK fechado"),
            self._check("approval_route", "Aprovações acessíveis", files["approval_cockpit_present"], "/app/mobile-approval-cockpit-v2 existe"),
            self._check("apk_project", "Projeto Android existe", files["android_project_present"], "android-app/ pronto para build"),
            self._check("apk_workflow", "Build APK canónico existe", files["apk_workflow_present"], "workflow Android APK Build presente"),
            self._check("exe_workflow", "Build EXE canónico existe", files["exe_workflow_present"], "workflow Windows EXE Build presente"),
        ]
        passed = sum(1 for item in checks if item["ok"])
        failed = len(checks) - passed
        readiness_score = round((passed / len(checks)) * 100) if checks else 0
        status = "ready" if failed == 0 else ("almost_ready" if readiness_score >= 75 else "not_ready")
        blockers = [item for item in checks if not item["ok"]]
        next_action = self._next_action(status, blockers, pc)
        return {
            "ok": True,
            "mode": "ready_to_use_home_check",
            "status": status,
            "readiness_score": readiness_score,
            "passed_count": passed,
            "failed_count": failed,
            "checks": checks,
            "blockers": blockers,
            "next_action": next_action,
            "home_summary": {
                "home_route_present": files["home_backend_route_present"],
                "apk_home_entry": files["apk_home_entry"],
                "active_project": priority.get("active_project"),
            },
            "pc_autopilot": {
                "status": pc.get("status"),
                "enabled": pc.get("settings", {}).get("enabled"),
                "apk_disconnect_safe": pc.get("apk_disconnect_safe"),
            },
        }

    def _check(self, check_id: str, label: str, ok: bool, detail: str) -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok), "detail": detail}

    def _file_checks(self) -> Dict[str, bool]:
        main_activity = Path("android-app/app/src/main/java/pt/andrevazao/godmode/MainActivity.java")
        main_activity_text = main_activity.read_text(encoding="utf-8") if main_activity.exists() else ""
        home_route = Path("backend/app/routes/god_mode_home.py")
        home_frontend = Path("backend/app/routes/god_mode_home_frontend.py")
        route_files = [Path("backend/app/routes/mobile_approval_cockpit_v2_frontend.py"), Path("backend/app/routes/mobile_approval_cockpit_v2.py")]
        return {
            "apk_home_entry": 'ENTRY_ROUTE = "/app/home"' in main_activity_text,
            "home_backend_route_present": home_route.exists() and home_frontend.exists(),
            "approval_cockpit_present": any(path.exists() for path in route_files),
            "android_project_present": Path("android-app/app/build.gradle").exists() and main_activity.exists(),
            "apk_workflow_present": Path(".github/workflows/android-real-build-progressive.yml").exists(),
            "exe_workflow_present": Path(".github/workflows/windows-exe-build.yml").exists(),
        }

    def _next_action(self, status: str, blockers: List[Dict[str, Any]], pc: Dict[str, Any]) -> Dict[str, Any]:
        if blockers:
            return {"label": "Resolver blockers antes de instalar/usar", "route": "/app/home", "kind": "fix_blockers", "blocker_count": len(blockers)}
        if pc.get("status") == "disabled":
            return {"label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot", "kind": "start_pc_autopilot"}
        return {"label": "Abrir Home e dar a próxima ordem", "route": "/app/home", "kind": "use_god_mode"}

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        checklist = self.build_checklist(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "ready_to_use_home_check_status",
            "status": checklist["status"],
            "readiness_score": checklist["readiness_score"],
            "failed_count": checklist["failed_count"],
            "next_action": checklist["next_action"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "ready_to_use_home_check_package", "package": {"status": self.get_status(tenant_id), "checklist": self.build_checklist(tenant_id)}}


ready_to_use_home_check_service = ReadyToUseHomeCheckService()
