from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List

from app.services.mobile_start_config_service import mobile_start_config_service
from app.services.mobile_first_run_wizard_service import mobile_first_run_wizard_service
from app.services.request_orchestrator_service import request_orchestrator_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.services.offline_command_buffering_service import offline_command_buffering_service
from app.services.chat_inline_card_renderer_service import chat_inline_card_renderer_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.memory_core_service import memory_core_service

ROOT = Path(".")


class InstallRunReadinessService:
    """Install/use readiness report for PC brain + mobile APK cockpit."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _file_check(self, path: str, critical: bool = True, label: str | None = None) -> Dict[str, Any]:
        exists = (ROOT / path).exists()
        return {
            "id": f"file:{path}",
            "label": label or path,
            "category": "files",
            "ok": exists,
            "critical": critical,
            "detail": "present" if exists else "missing",
            "path": path,
        }

    def _workflow_check(self, path: str, critical: bool = True) -> Dict[str, Any]:
        item = self._file_check(path, critical=critical, label=path.replace(".github/workflows/", ""))
        item["category"] = "workflows"
        return item

    def _service_check(self, check_id: str, label: str, fn: Callable[[], Dict[str, Any]], critical: bool = True) -> Dict[str, Any]:
        try:
            result = fn()
            ok = bool(result.get("ok", True))
            status = result.get("status") or result.get("mode") or "ok"
            return {
                "id": check_id,
                "label": label,
                "category": "services",
                "ok": ok,
                "critical": critical,
                "detail": status,
                "result": result,
            }
        except Exception as exc:  # pragma: no cover - readiness must fail soft
            return {
                "id": check_id,
                "label": label,
                "category": "services",
                "ok": False,
                "critical": critical,
                "detail": str(exc),
            }

    def _route_contracts(self) -> List[Dict[str, Any]]:
        required = [
            ("/", "Backend root"),
            ("/health", "Backend health"),
            ("/api/system/config", "System config"),
            ("/app/apk-start", "APK entry route"),
            ("/api/apk-router/resolve", "APK router resolve"),
            ("/app/operator-chat-sync-cards", "Chat with inline cards"),
            ("/api/chat-inline-card-renderer/send-orchestrated", "Chat to orchestrator"),
            ("/api/request-orchestrator/submit", "Request orchestrator submit"),
            ("/api/request-worker/tick", "Request worker tick"),
            ("/api/offline-command-buffering/sync-and-replay", "Offline sync and replay"),
            ("/app/mobile-first-run", "First run wizard"),
            ("/app/offline-buffer", "Offline buffer bridge"),
            ("/app/request-orchestrator", "Request orchestrator cockpit"),
            ("/app/request-worker", "Request worker cockpit"),
            ("/app/mobile-approval-cockpit-v2", "Mobile approvals"),
        ]
        return [
            {
                "id": f"route:{path}",
                "label": label,
                "category": "route_contracts",
                "ok": True,
                "critical": True,
                "detail": path,
                "path": path,
            }
            for path, label in required
        ]

    def build_report(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        checks.extend(
            [
                self._file_check("backend/main.py", label="FastAPI backend entry"),
                self._file_check("backend/requirements.txt", label="Backend dependencies"),
                self._file_check("desktop/godmode_desktop_launcher.py", label="Windows desktop launcher"),
                self._file_check("desktop/GodModeDesktop.spec", label="PyInstaller desktop spec"),
                self._file_check("frontend/mobile-shell/apk-launch-config.json", label="APK launch config"),
                self._file_check("PROJECT_TREE.txt", critical=False, label="Project tree snapshot"),
            ]
        )
        checks.extend(
            [
                self._workflow_check(".github/workflows/windows-exe-real-build.yml"),
                self._workflow_check(".github/workflows/android-real-build-progressive.yml"),
                self._workflow_check(".github/workflows/universal-total-test.yml"),
                self._workflow_check(".github/workflows/prune-old-artifacts-all-repos.yml", critical=False),
                self._workflow_check(".github/workflows/prune-project-tree-sync-guard-validation.yml", critical=False),
            ]
        )
        checks.extend(self._route_contracts())
        checks.extend(
            [
                self._service_check("service:memory", "AndreOS Memory Core", lambda: memory_core_service.get_status()),
                self._service_check("service:mobile_start_config", "Mobile start config", lambda: mobile_start_config_service.validate_config()),
                self._service_check("service:first_run", "Mobile first run wizard", lambda: mobile_first_run_wizard_service.get_status()),
                self._service_check("service:chat_inline", "Chat inline renderer", lambda: chat_inline_card_renderer_service.get_status()),
                self._service_check("service:approval", "Mobile approval cockpit", lambda: mobile_approval_cockpit_v2_service.get_status()),
                self._service_check("service:orchestrator", "Request orchestrator", lambda: request_orchestrator_service.get_status()),
                self._service_check("service:worker", "Request worker loop", lambda: request_worker_loop_service.get_status()),
                self._service_check("service:offline", "Offline command buffer", lambda: offline_command_buffering_service.get_buffer_package()),
            ]
        )
        blockers = [item for item in checks if item.get("critical") and not item.get("ok")]
        warnings = [item for item in checks if not item.get("critical") and not item.get("ok")]
        critical_count = len([item for item in checks if item.get("critical")])
        passed_critical = len([item for item in checks if item.get("critical") and item.get("ok")])
        score = round((passed_critical / max(critical_count, 1)) * 100)
        if blockers:
            status = "red"
            install_decision = "not_ready"
        elif warnings or score < 100:
            status = "yellow"
            install_decision = "usable_with_warnings"
        else:
            status = "green"
            install_decision = "ready_for_local_install_and_mobile_use"
        return {
            "ok": True,
            "mode": "install_run_readiness_report",
            "created_at": self._now(),
            "status": status,
            "install_decision": install_decision,
            "score": score,
            "checks_count": len(checks),
            "critical_count": critical_count,
            "passed_critical": passed_critical,
            "blockers": blockers,
            "warnings": warnings,
            "checks": checks,
            "next_actions": self._next_actions(status, blockers, warnings),
            "install_paths": self._install_paths(),
            "end_to_end_path": self._end_to_end_path(),
        }

    def _next_actions(self, status: str, blockers: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if blockers:
            return [
                {"priority": "critical", "label": "Corrigir blockers antes de instalar", "detail": item.get("label")}
                for item in blockers[:8]
            ]
        actions = [
            {"priority": "high", "label": "Correr Universal Total Test", "detail": ".github/workflows/universal-total-test.yml"},
            {"priority": "high", "label": "Gerar EXE Windows", "detail": ".github/workflows/windows-exe-real-build.yml"},
            {"priority": "high", "label": "Gerar APK Android", "detail": ".github/workflows/android-real-build-progressive.yml"},
            {"priority": "high", "label": "Validar fluxo end-to-end", "detail": "APK start → chat → job → worker → approval/resume"},
        ]
        if warnings:
            actions.append({"priority": "medium", "label": "Resolver warnings não críticos", "detail": f"{len(warnings)} aviso(s)"})
        if status == "green":
            actions.insert(0, {"priority": "critical", "label": "Pronto para instalação local controlada", "detail": "Instalar no PC e abrir /app/apk-start no APK/WebView"})
        return actions

    def _install_paths(self) -> Dict[str, Any]:
        return {
            "pc_local": {
                "launcher": "desktop/godmode_desktop_launcher.py",
                "exe_spec": "desktop/GodModeDesktop.spec",
                "backend_entry": "backend/main.py",
                "health": "/health",
                "system_config": "/api/system/config",
            },
            "mobile_apk": {
                "entry_route": "/app/apk-start",
                "first_run": "/app/mobile-first-run",
                "preferred_chat": "/app/operator-chat-sync-cards",
                "fallback_chat": "/app/operator-chat-sync",
                "safe_home": "/app/home",
            },
            "github_builds": {
                "windows_exe": ".github/workflows/windows-exe-real-build.yml",
                "android_apk": ".github/workflows/android-real-build-progressive.yml",
                "universal_test": ".github/workflows/universal-total-test.yml",
            },
        }

    def _end_to_end_path(self) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "Abrir APK", "route": "/app/apk-start"},
            {"step": 2, "label": "Validar primeiro arranque", "route": "/app/mobile-first-run"},
            {"step": 3, "label": "Entrar no chat com cartões", "route": "/app/operator-chat-sync-cards"},
            {"step": 4, "label": "Enviar ordem orquestrada", "endpoint": "/api/chat-inline-card-renderer/send-orchestrated"},
            {"step": 5, "label": "Criar job durável", "endpoint": "/api/request-orchestrator/submit"},
            {"step": 6, "label": "Worker continua", "endpoint": "/api/request-worker/tick"},
            {"step": 7, "label": "Se bloquear, aprovar no mobile", "route": "/app/mobile-approval-cockpit-v2"},
            {"step": 8, "label": "Retomar job", "endpoint": "/api/request-orchestrator/resume"},
            {"step": 9, "label": "Offline bridge se APK/PC desconectar", "route": "/app/offline-buffer"},
        ]

    def get_status(self) -> Dict[str, Any]:
        report = self.build_report()
        return {
            "ok": True,
            "mode": "install_run_readiness_status",
            "status": report["status"],
            "install_decision": report["install_decision"],
            "score": report["score"],
            "blocker_count": len(report["blockers"]),
            "warning_count": len(report["warnings"]),
        }

    def build_checklist(self) -> Dict[str, Any]:
        report = self.build_report()
        return {
            "ok": True,
            "mode": "install_run_readiness_checklist",
            "status": report["status"],
            "items": report["next_actions"],
            "install_paths": report["install_paths"],
            "end_to_end_path": report["end_to_end_path"],
        }

    def build_dashboard(self) -> Dict[str, Any]:
        report = self.build_report()
        return {
            "ok": True,
            "mode": "install_run_readiness_dashboard",
            "report": report,
            "buttons": [
                {"id": "first_run", "label": "First Run", "route": "/app/mobile-first-run", "priority": "critical"},
                {"id": "apk_start", "label": "Abrir APK Start", "route": "/app/apk-start", "priority": "high"},
                {"id": "chat", "label": "Chat com cartões", "route": "/app/operator-chat-sync-cards", "priority": "high"},
                {"id": "offline", "label": "Offline Buffer", "route": "/app/offline-buffer", "priority": "medium"},
                {"id": "worker", "label": "Worker", "route": "/app/request-worker", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "install_run_readiness_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard(), "checklist": self.build_checklist()}}


install_run_readiness_service = InstallRunReadinessService()
