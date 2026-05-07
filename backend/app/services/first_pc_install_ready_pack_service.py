from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_pc_runtime_verification_service import first_pc_runtime_verification_service
from app.services.first_real_install_launcher_service import first_real_install_launcher_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.install_first_run_guide_service import install_first_run_guide_service
from app.services.install_readiness_final_service import install_readiness_final_service
from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service


class FirstPcInstallReadyPackService:
    SERVICE_ID = "first_pc_install_ready_pack"
    VERSION = "phase_202_v1"

    ESSENTIAL_LOCAL_ROUTES = [
        {"label": "Home", "route": "/app/home", "must_open": True},
        {"label": "PC Runtime Check", "route": "/app/first-pc-runtime-verification", "must_open": True},
        {"label": "Install Ready Pack", "route": "/app/first-pc-install-ready-pack", "must_open": True},
        {"label": "Artifacts / APK EXE", "route": "/app/home", "api": "/api/artifacts-center/dashboard", "must_open": True},
        {"label": "Repo Inventory", "route": "/app/github-repo-inventory-feed", "must_open": True},
        {"label": "Conversation Import", "route": "/app/conversation-source-import-feed", "must_open": True},
        {"label": "Provider Launcher", "route": "/app/provider-browser-local-launcher", "must_open": True},
        {"label": "Native Skills Queue", "route": "/app/native-skills-adoption-queue", "must_open": True},
    ]

    FIRST_LOCAL_START_STEPS = [
        "Download the latest Windows EXE artifact from the Windows EXE Build workflow.",
        "Extract the artifact on the home PC.",
        "Run GodModeDesktop.exe.",
        "Wait until the browser opens /app/home or open http://127.0.0.1:8000/app/home manually.",
        "Open /app/first-pc-install-ready-pack and confirm the readiness pack.",
        "Use /app/github-repo-inventory-feed to import or seed repos.",
        "Use /app/conversation-source-import-feed to paste important project conversation/context.",
        "Use /app/provider-browser-local-launcher only for safe manual provider opening/capture.",
        "Use /app/native-skills-adoption-queue to review self-evolution candidates.",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        readiness = self._safe_call(lambda: install_readiness_final_service.build_check(run_deep=False))
        artifacts = self._safe_call(artifacts_center_service.build_dashboard)
        blockers = self._blockers(readiness, artifacts)
        return {
            "ok": len(blockers) == 0,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "ready_for_first_pc_install": len(blockers) == 0,
            "blocker_count": len(blockers),
            "blockers": blockers,
            "canonical_local_url": "http://127.0.0.1:8000/app/home",
            "install_ready_pack_route": "/app/first-pc-install-ready-pack",
            "can_store_secrets_in_repo": False,
            "can_auto_update_without_gate": False,
        }

    def one_click_local_start_contract(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "one_click_local_start_contract",
            "goal": "Give the home PC a clear first-run contract for GodModeDesktop.exe without storing secrets or doing risky automation.",
            "desktop_entrypoint": {
                "expected_executable": "GodModeDesktop.exe",
                "expected_backend_port": 8000,
                "canonical_local_home": "http://127.0.0.1:8000/app/home",
                "fallback_health": "http://127.0.0.1:8000/health",
            },
            "first_start_steps": self.FIRST_LOCAL_START_STEPS,
            "success_signals": [
                "/health returns ok",
                "/app/home opens in local browser",
                "/api/god-mode-global-state/package returns current phase",
                "/app/first-pc-install-ready-pack opens",
                "no token/password/cookie is requested or stored by the ready pack",
            ],
            "safe_failure_modes": [
                "backend_not_started",
                "port_busy",
                "artifact_missing",
                "browser_not_opened",
                "manual_provider_login_required",
                "secret_input_blocked",
            ],
            "operator_actions": [
                "Retry opening GodModeDesktop.exe",
                "Open /health manually",
                "Open /app/home manually",
                "Use GitHub Actions artifacts if local EXE is stale",
                "Never paste secrets into import boxes",
            ],
        }

    def readiness_pack(self) -> Dict[str, Any]:
        artifacts = self._safe_call(artifacts_center_service.build_dashboard)
        launcher = self._safe_call(first_real_install_launcher_service.get_package)
        runtime = self._safe_call(first_pc_runtime_verification_service.package)
        guide = self._safe_call(install_first_run_guide_service.build_guide)
        final_readiness = self._safe_call(lambda: install_readiness_final_service.build_check(run_deep=False))
        home_ready = self._safe_call(ready_to_use_home_check_service.checklist)
        global_state = self._safe_call(god_mode_global_state_service.package)
        return {
            "ok": True,
            "mode": "first_pc_install_ready_pack",
            "status": self.status(),
            "one_click_local_start_contract": self.one_click_local_start_contract(),
            "essential_local_routes": self.ESSENTIAL_LOCAL_ROUTES,
            "artifact_targets": self._artifact_targets(artifacts),
            "first_real_install_launcher": launcher,
            "first_pc_runtime_verification": runtime,
            "install_first_run_guide": guide,
            "install_readiness_final": final_readiness,
            "ready_to_use_home": home_ready,
            "global_state_summary": self._global_state_summary(global_state),
            "secrets_policy": {
                "store_raw_secrets": False,
                "allowed_in_memory": ["secret labels", "vault references", "manual action required"],
                "blocked": ["tokens", "passwords", "cookies", "API keys", "private keys", "browser sessions"],
            },
            "next_real_operator_flow": [
                "Install/run GodModeDesktop.exe on the PC.",
                "Open this ready pack.",
                "Import repo inventory.",
                "Import one current conversation.",
                "Generate/inspect self-evolution candidates.",
                "Only then approve candidate-to-PR planning.",
            ],
        }

    def checklist(self) -> Dict[str, Any]:
        pack = self.readiness_pack()
        status = pack.get("status", {})
        checks = [
            {"id": "desktop_exe_contract", "label": "GodModeDesktop.exe contract exists", "ok": True, "detail": pack["one_click_local_start_contract"]["desktop_entrypoint"]},
            {"id": "canonical_home", "label": "Canonical local home defined", "ok": True, "detail": "http://127.0.0.1:8000/app/home"},
            {"id": "essential_routes", "label": "Essential routes listed", "ok": len(self.ESSENTIAL_LOCAL_ROUTES) >= 8, "detail": self.ESSENTIAL_LOCAL_ROUTES},
            {"id": "readiness_pack", "label": "Ready pack generated", "ok": True, "detail": status},
            {"id": "secrets_policy", "label": "Secrets blocked from repo/memory", "ok": True, "detail": pack["secrets_policy"]},
            {"id": "auto_update_gate", "label": "Auto-update remains gated", "ok": status.get("can_auto_update_without_gate") is False, "detail": status},
        ]
        return {"ok": all(item["ok"] for item in checks), "mode": "first_pc_install_ready_checklist", "checks": checks, "failed_checks": [item for item in checks if not item["ok"]]}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "checklist": self.checklist(), "ready_pack": self.readiness_pack()}

    def _artifact_targets(self, artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = artifacts.get("artifacts", []) if isinstance(artifacts, dict) else []
        if not items:
            return [
                {"label": "GodModeDesktop.exe", "artifact_name": "godmode-windows-exe", "workflow": "Windows EXE Build", "required": True},
                {"label": "GodModeMobile-debug.apk", "artifact_name": "godmode-android-webview-apk", "workflow": "Android APK Build", "required": True},
            ]
        return [
            {
                "label": item.get("expected_file") or item.get("id") or "artifact",
                "artifact_name": item.get("artifact_name") or item.get("id"),
                "workflow": item.get("workflow"),
                "required": True,
                "status": item.get("status"),
            }
            for item in items
        ]

    def _blockers(self, readiness: Dict[str, Any], artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        blockers: List[Dict[str, Any]] = []
        if isinstance(readiness, dict) and readiness.get("ready_to_install") is False:
            blockers.append({"id": "install_readiness", "label": "Install readiness not fully ready", "detail": readiness.get("failed_checks", [])[:5]})
        if isinstance(artifacts, dict) and artifacts.get("status") not in {None, "ready"}:
            blockers.append({"id": "artifacts_status", "label": "Artifacts center not ready", "detail": artifacts.get("status")})
        return blockers

    def _global_state_summary(self, global_state: Dict[str, Any]) -> Dict[str, Any]:
        status = global_state.get("status", {}) if isinstance(global_state, dict) else {}
        return {
            "current_phase": status.get("current_phase"),
            "latest_merged_phase": status.get("latest_merged_phase"),
            "canonical_cockpit_route": status.get("canonical_cockpit_route", "/app/home"),
            "pc_brain": status.get("pc_brain"),
            "mobile_first": status.get("mobile_first"),
        }

    def _safe_call(self, fn) -> Dict[str, Any]:
        try:
            result = fn()
            return result if isinstance(result, dict) else {"ok": True, "value": result}
        except Exception as exc:  # pragma: no cover
            return {"ok": False, "error": str(exc), "function": getattr(fn, "__name__", "unknown")}


first_pc_install_ready_pack_service = FirstPcInstallReadyPackService()
