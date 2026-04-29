from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
READINESS_FILE = DATA_DIR / "final_install_readiness_v2.json"
READINESS_STORE = AtomicJsonStore(
    READINESS_FILE,
    default_factory=lambda: {
        "version": 2,
        "policy": "final_gate_before_operator_installs_real_apk_exe",
        "checks": [],
    },
)


class FinalInstallReadinessV2Service:
    """Final install readiness gate before the operator installs EXE/APK.

    This gate is stricter than earlier readiness checks. It is meant to answer:
    "Can Andre install the God Mode on PC/phone now and start real use?"
    """

    WORKFLOWS = [
        {
            "id": "android_apk_workflow",
            "label": "Android APK workflow",
            "path": ".github/workflows/android-real-build-progressive.yml",
            "must_contain": ["assembleDebug", "GodModeMobile-debug.apk", "upload-artifact"],
            "weight": 10,
            "critical": True,
        },
        {
            "id": "windows_exe_workflow",
            "label": "Windows EXE workflow",
            "path": ".github/workflows/windows-exe-real-build.yml",
            "must_contain": ["pyinstaller", "GodModeDesktop.exe", "upload-artifact"],
            "weight": 10,
            "critical": True,
        },
    ]

    SERVICE_CHECKS = [
        {
            "id": "home_easy_mode",
            "label": "Home / Modo Fácil",
            "import_path": "app.services.home_operator_ux_service.home_operator_ux_service",
            "endpoint": "/api/home-operator-ux/panel",
            "weight": 8,
            "critical": True,
        },
        {
            "id": "critical_actions_hub",
            "label": "Ações críticas",
            "import_path": "app.services.home_critical_actions_hub_service.home_critical_actions_hub_service",
            "endpoint": "/api/home-critical-actions/panel",
            "weight": 8,
            "critical": True,
        },
        {
            "id": "install_smoke_test",
            "label": "Smoke test CI seguro",
            "import_path": "app.services.real_install_smoke_test_service.real_install_smoke_test_service",
            "method": "run_ci_safe",
            "endpoint": "/api/real-install-smoke-test/ci-safe",
            "weight": 12,
            "critical": True,
        },
        {
            "id": "apk_pc_pairing",
            "label": "Pairing APK ↔ PC",
            "import_path": "app.services.apk_pc_pairing_wizard_service.apk_pc_pairing_wizard_service",
            "endpoint": "/api/apk-pc-pairing/panel",
            "weight": 8,
            "critical": True,
        },
        {
            "id": "resumable_jobs",
            "label": "Jobs retomáveis",
            "import_path": "app.services.resumable_job_checkpoint_engine_service.resumable_job_checkpoint_engine_service",
            "endpoint": "/api/resumable-jobs/panel",
            "weight": 8,
            "critical": True,
        },
        {
            "id": "self_update",
            "label": "Self-update",
            "import_path": "app.services.self_update_manager_service.self_update_manager_service",
            "endpoint": "/api/self-update/panel",
            "weight": 8,
            "critical": True,
        },
        {
            "id": "mobile_update",
            "label": "Mobile APK update",
            "import_path": "app.services.mobile_apk_update_orchestrator_service.mobile_apk_update_orchestrator_service",
            "endpoint": "/api/mobile-apk-update/panel",
            "weight": 7,
            "critical": True,
        },
        {
            "id": "project_registry",
            "label": "Project Memory Registry",
            "import_path": "app.services.project_memory_registry_service.project_memory_registry_service",
            "endpoint": "/api/project-memory-registry/panel",
            "weight": 7,
            "critical": True,
        },
        {
            "id": "browser_provider_execution",
            "label": "Browser/provider execution",
            "import_path": "app.services.browser_provider_execution_hub_service.browser_provider_execution_hub_service",
            "endpoint": "/api/browser-provider-execution/panel",
            "weight": 6,
            "critical": False,
        },
        {
            "id": "repo_file_patch",
            "label": "Repo/file patch hub",
            "import_path": "app.services.repo_file_patch_hub_service.repo_file_patch_hub_service",
            "endpoint": "/api/repo-file-patch/panel",
            "weight": 6,
            "critical": False,
        },
        {
            "id": "completion_scorecard",
            "label": "Estado real %",
            "import_path": "app.services.god_mode_real_completion_scorecard_service.god_mode_real_completion_scorecard_service",
            "endpoint": "/api/god-mode-completion/panel",
            "weight": 5,
            "critical": False,
        },
        {
            "id": "artifacts_center",
            "label": "Artifacts Center",
            "import_path": "app.services.artifacts_center_service.artifacts_center_service",
            "endpoint": "/api/artifacts-center/dashboard",
            "weight": 5,
            "critical": True,
        },
        {
            "id": "install_first_run_guide",
            "label": "Install First Run Guide",
            "import_path": "app.services.install_first_run_service.install_first_run_service",
            "endpoint": "/api/install-first-run/guide",
            "weight": 5,
            "critical": False,
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _service_status(self, check: Dict[str, Any]) -> Dict[str, Any]:
        try:
            module_name, service_name = check["import_path"].rsplit(".", 1)
            service = getattr(__import__(module_name, fromlist=[service_name]), service_name)
            method_name = check.get("method") or "get_status"
            if hasattr(service, method_name):
                value = getattr(service, method_name)()
            elif hasattr(service, "panel"):
                value = service.panel()
            else:
                value = {"ok": True, "note": "imported"}
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:500]}

    def _workflow_status(self, check: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(check["path"])
        if not path.exists():
            return {"ok": False, "error": "workflow_missing", "path": str(path)}
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [needle for needle in check.get("must_contain", []) if needle not in text]
        return {"ok": not missing, "missing": missing, "path": str(path)}

    def run_check(self) -> Dict[str, Any]:
        service_results = []
        for check in self.SERVICE_CHECKS:
            status = self._service_status(check)
            service_results.append(self._result_item(check, status))
        workflow_results = []
        for check in self.WORKFLOWS:
            status = self._workflow_status(check)
            workflow_results.append(self._result_item(check, status))
        results = service_results + workflow_results
        score = self._score(results)
        blockers = [item for item in results if item.get("critical") and not item.get("ok")]
        warnings = [item for item in results if not item.get("critical") and not item.get("ok")]
        decision = self._decision(score=score, blockers=blockers, warnings=warnings)
        check_run = {
            "check_id": f"final-install-readiness-v2-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "final_install_readiness_v2",
            "score_percent": score,
            "decision": decision,
            "ready_to_install_real": decision["ready_to_install_real"],
            "blockers": blockers,
            "warnings": warnings,
            "service_results": service_results,
            "workflow_results": workflow_results,
            "operator_install_contract": self.install_contract().get("contract"),
            "next_action": self._next_action(decision, blockers),
        }
        self._store(check_run)
        return {"ok": True, "mode": "final_install_readiness_v2", "check": check_run}

    def _result_item(self, check: Dict[str, Any], status: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": check["id"],
            "label": check["label"],
            "endpoint": check.get("endpoint"),
            "path": check.get("path"),
            "weight": check.get("weight", 1),
            "critical": bool(check.get("critical", False)),
            "ok": bool(status.get("ok", False)),
            "status": status,
        }

    def _score(self, results: List[Dict[str, Any]]) -> int:
        total = sum(item.get("weight", 1) for item in results) or 1
        earned = sum(item.get("weight", 1) for item in results if item.get("ok"))
        return round((earned / total) * 100)

    def _decision(self, score: int, blockers: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        if blockers:
            return {
                "ready_to_install_real": False,
                "label": "não instalar ainda",
                "reason": "existem blockers críticos",
                "confidence": "high",
            }
        if score >= 92:
            return {
                "ready_to_install_real": True,
                "label": "podes instalar para primeiro teste real",
                "reason": "gate final verde",
                "confidence": "high" if not warnings else "medium",
            }
        if score >= 85:
            return {
                "ready_to_install_real": True,
                "label": "podes instalar com cautela",
                "reason": "sem blockers críticos, mas ainda há warnings",
                "confidence": "medium",
            }
        return {
            "ready_to_install_real": False,
            "label": "aguardar mais correções",
            "reason": "score abaixo do mínimo recomendado",
            "confidence": "medium",
        }

    def _next_action(self, decision: Dict[str, Any], blockers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if blockers:
            first = blockers[0]
            return {
                "label": f"Corrigir blocker: {first.get('label')}",
                "endpoint": first.get("endpoint") or "/api/final-install-readiness-v2/panel",
                "priority": "critical",
            }
        if decision.get("ready_to_install_real"):
            return {
                "label": "Abrir Download/Install Center v2",
                "endpoint": "/api/download-install-center-v2/panel",
                "priority": "critical",
            }
        return {
            "label": "Reexecutar gate final depois das correções",
            "endpoint": "/api/final-install-readiness-v2/check",
            "priority": "high",
        }

    def install_contract(self) -> Dict[str, Any]:
        contract = {
            "contract_id": f"final-install-contract-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "steps": [
                {"step": 1, "label": "baixar GodModeDesktop.exe", "source": "Windows EXE artifact"},
                {"step": 2, "label": "baixar GodModeMobile-debug.apk", "source": "Android APK artifact"},
                {"step": 3, "label": "executar EXE no PC", "expected": "backend online"},
                {"step": 4, "label": "abrir pairing no PC", "endpoint": "/api/apk-pc-pairing/start"},
                {"step": 5, "label": "instalar/abrir APK no telemóvel", "expected": "pairing confirm + heartbeat"},
                {"step": 6, "label": "abrir Modo Fácil", "endpoint": "/api/home-operator-ux/panel"},
                {"step": 7, "label": "correr smoke local", "endpoint": "/api/real-install-smoke-test/local-contract"},
                {"step": 8, "label": "validar self-update e mobile update", "endpoint": "/api/self-update/panel"},
            ],
            "do_not_install_if": [
                "gate final tem blockers críticos",
                "APK/EXE artifacts não existem",
                "smoke CI falha",
                "pairing não existe",
                "registry de projetos falha",
            ],
        }
        return {"ok": True, "mode": "final_install_contract", "contract": contract}

    def _store(self, run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("checks", [])
            state["checks"].append(run)
            state["checks"] = state["checks"][-100:]
            return state
        READINESS_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        checks = READINESS_STORE.load().get("checks") or []
        return {
            "ok": True,
            "mode": "final_install_readiness_v2_latest",
            "latest_check": checks[-1] if checks else None,
            "check_count": len(checks),
        }

    def panel(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_check")
        return {
            "ok": True,
            "mode": "final_install_readiness_v2_panel",
            "headline": "Gate final antes de instalar God Mode",
            "latest": latest,
            "install_contract": self.install_contract().get("contract"),
            "safe_buttons": [
                {"id": "check", "label": "Verificar pronto para instalar", "endpoint": "/api/final-install-readiness-v2/check", "priority": "critical"},
                {"id": "contract", "label": "Contrato instalação", "endpoint": "/api/final-install-readiness-v2/install-contract", "priority": "high"},
                {"id": "latest", "label": "Último resultado", "endpoint": "/api/final-install-readiness-v2/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_check")
        if not latest:
            latest = self.run_check().get("check")
        return {
            "ok": True,
            "mode": "final_install_readiness_v2_status",
            "score_percent": latest.get("score_percent"),
            "ready_to_install_real": latest.get("ready_to_install_real"),
            "decision": latest.get("decision"),
            "blocker_count": len(latest.get("blockers") or []),
            "warning_count": len(latest.get("warnings") or []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "final_install_readiness_v2_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


final_install_readiness_v2_service = FinalInstallReadinessV2Service()
