from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SMOKE_FILE = DATA_DIR / "real_install_smoke_test.json"
SMOKE_STORE = AtomicJsonStore(
    SMOKE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "ci_first_then_local_real_install_smoke_test",
        "runs": [],
    },
)


class RealInstallSmokeTestService:
    """Smoke tests for install readiness without forcing PC/APK install.

    The service has two levels:
    - ci_safe: checks backend modules/routes/contracts/workflow references.
    - local_contract: tells the installed EXE/APK what to verify after real install.
    """

    CRITICAL_SERVICES = [
        {
            "id": "home_operator_ux",
            "import_path": "app.services.home_operator_ux_service.home_operator_ux_service",
            "endpoint": "/api/home-operator-ux/panel",
        },
        {
            "id": "home_critical_actions",
            "import_path": "app.services.home_critical_actions_hub_service.home_critical_actions_hub_service",
            "endpoint": "/api/home-critical-actions/panel",
        },
        {
            "id": "completion_scorecard",
            "import_path": "app.services.god_mode_real_completion_scorecard_service.god_mode_real_completion_scorecard_service",
            "endpoint": "/api/god-mode-completion/panel",
        },
        {
            "id": "apk_pc_pairing",
            "import_path": "app.services.apk_pc_pairing_wizard_service.apk_pc_pairing_wizard_service",
            "endpoint": "/api/apk-pc-pairing/panel",
        },
        {
            "id": "resumable_jobs",
            "import_path": "app.services.resumable_job_checkpoint_engine_service.resumable_job_checkpoint_engine_service",
            "endpoint": "/api/resumable-jobs/panel",
        },
        {
            "id": "browser_provider_execution",
            "import_path": "app.services.browser_provider_execution_hub_service.browser_provider_execution_hub_service",
            "endpoint": "/api/browser-provider-execution/panel",
        },
        {
            "id": "repo_file_patch",
            "import_path": "app.services.repo_file_patch_hub_service.repo_file_patch_hub_service",
            "endpoint": "/api/repo-file-patch/panel",
        },
        {
            "id": "pc_migration",
            "import_path": "app.services.pc_migration_control_center_service.pc_migration_control_center_service",
            "endpoint": "/api/pc-migration-control/panel",
        },
        {
            "id": "autonomous_delivery",
            "import_path": "app.services.autonomous_install_research_code_service.autonomous_install_research_code_service",
            "endpoint": "/api/autonomous-delivery/panel",
        },
    ]

    WORKFLOW_EXPECTATIONS = [
        {
            "id": "android_apk",
            "path": ".github/workflows/android-real-build-progressive.yml",
            "must_contain": ["assembleDebug", "GodModeMobile-debug.apk", "upload-artifact", "real_webview_shell_apk"],
        },
        {
            "id": "windows_exe",
            "path": ".github/workflows/windows-exe-real-build.yml",
            "must_contain": ["pyinstaller", "GodModeDesktop.exe", "upload-artifact", "desktop-installer-manifest.json"],
        },
    ]

    LOCAL_INSTALL_STEPS = [
        {"step": 1, "label": "Abrir GodModeDesktop.exe", "expected": "backend online"},
        {"step": 2, "label": "Abrir /api/apk-pc-pairing/start", "expected": "pairing session created"},
        {"step": 3, "label": "Abrir APK e confirmar pairing", "expected": "confirmation + heartbeat"},
        {"step": 4, "label": "Abrir Modo Fácil", "expected": "Home responds"},
        {"step": 5, "label": "Abrir Ações críticas", "expected": "critical hub responds"},
        {"step": 6, "label": "Criar job teste", "expected": "resumable job created"},
        {"step": 7, "label": "Criar checkpoint teste", "expected": "checkpoint safe_to_resume"},
        {"step": 8, "label": "Completar job teste", "expected": "job completed"},
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_call_status(self, item: Dict[str, Any]) -> Dict[str, Any]:
        try:
            module_name, service_name = item["import_path"].rsplit(".", 1)
            service = getattr(__import__(module_name, fromlist=[service_name]), service_name)
            if hasattr(service, "get_status"):
                value = service.get_status()
            elif hasattr(service, "panel"):
                value = service.panel()
            else:
                value = {"ok": True, "note": "service imported but no status/panel"}
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def run_ci_safe(self) -> Dict[str, Any]:
        service_checks = []
        for service in self.CRITICAL_SERVICES:
            status = self._safe_call_status(service)
            service_checks.append({
                "id": service["id"],
                "endpoint": service["endpoint"],
                "ok": bool(status.get("ok", False)),
                "status": status,
            })
        workflow_checks = [self._check_workflow(item) for item in self.WORKFLOW_EXPECTATIONS]
        local_contract = self.local_contract().get("contract")
        blockers = []
        for check in service_checks:
            if not check.get("ok"):
                blockers.append({"kind": "service", "id": check["id"], "reason": check.get("status", {}).get("error", "not_ok")})
        for check in workflow_checks:
            if not check.get("ok"):
                blockers.append({"kind": "workflow", "id": check["id"], "reason": check.get("reason")})
        run = {
            "run_id": f"install-smoke-ci-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "ci_safe",
            "ok": not blockers,
            "service_checks": service_checks,
            "workflow_checks": workflow_checks,
            "local_contract": local_contract,
            "blockers": blockers,
            "safe_for_operator_pc": True,
            "installs_anything": False,
            "operator_next": self._operator_next(blockers),
        }
        self._store_run(run)
        return {"ok": run["ok"], "mode": "real_install_smoke_test_ci_safe", "run": run}

    def _check_workflow(self, expectation: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(expectation["path"])
        if not path.exists():
            return {"id": expectation["id"], "path": str(path), "ok": False, "reason": "workflow_missing"}
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [needle for needle in expectation["must_contain"] if needle not in text]
        return {
            "id": expectation["id"],
            "path": str(path),
            "ok": not missing,
            "missing": missing,
            "reason": None if not missing else "expected_terms_missing",
        }

    def local_contract(self) -> Dict[str, Any]:
        contract = {
            "contract_id": f"install-smoke-local-contract-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "local_real_install_contract",
            "description": "Contrato de smoke test para quando o operador instalar EXE/APK reais.",
            "steps": self.LOCAL_INSTALL_STEPS,
            "success_criteria": [
                "EXE abre backend sem erro fatal",
                "pairing gera sessão curta",
                "APK confirma pairing e heartbeat",
                "Home/Modo Fácil abre",
                "Ações críticas abre",
                "job/checkpoint teste conclui",
                "nenhum secret é pedido no chat",
            ],
            "failure_policy": [
                "guardar erro em data/real_install_smoke_test.json",
                "mostrar próxima ação simples no APK/Home",
                "não apagar dados",
                "não reinstalar automaticamente sem OK",
                "se update falhar, manter versão anterior",
            ],
            "does_not_modify_projects": True,
        }
        return {"ok": True, "mode": "real_install_smoke_test_local_contract", "contract": contract}

    def _operator_next(self, blockers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if blockers:
            return {"label": "Corrigir blockers antes de instalar", "endpoint": "/api/real-install-smoke-test/ci-safe", "priority": "critical"}
        return {"label": "Pronto para build artifacts e smoke local quando decidires instalar", "endpoint": "/api/artifacts-center/dashboard", "priority": "high"}

    def _store_run(self, run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("runs", [])
            state["runs"].append(run)
            state["runs"] = state["runs"][-100:]
            return state
        SMOKE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = SMOKE_STORE.load()
        runs = state.get("runs") or []
        return {
            "ok": True,
            "mode": "real_install_smoke_test_latest",
            "latest_run": runs[-1] if runs else None,
            "run_count": len(runs),
        }

    def panel(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "real_install_smoke_test_panel",
            "headline": "Smoke test de instalação real",
            "latest": latest,
            "ci_safe": {
                "label": "Testar sem instalar no PC",
                "endpoint": "/api/real-install-smoke-test/ci-safe",
                "installs_anything": False,
            },
            "local_contract": self.local_contract().get("contract"),
            "safe_buttons": [
                {"id": "ci_safe", "label": "Smoke CI seguro", "endpoint": "/api/real-install-smoke-test/ci-safe", "priority": "critical"},
                {"id": "contract", "label": "Contrato local", "endpoint": "/api/real-install-smoke-test/local-contract", "priority": "high"},
                {"id": "latest", "label": "Último teste", "endpoint": "/api/real-install-smoke-test/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_run")
        return {
            "ok": True,
            "mode": "real_install_smoke_test_status",
            "has_run": latest is not None,
            "latest_ok": latest.get("ok") if latest else None,
            "installs_anything": False,
            "ci_safe_available": True,
            "local_contract_available": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "real_install_smoke_test_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


real_install_smoke_test_service = RealInstallSmokeTestService()
