from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Set

from app.services.andreos_memory_audit_service import andreos_memory_audit_service
from app.services.artifacts_center_service import artifacts_center_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.home_operator_ux_service import home_operator_ux_service
from app.services.project_tree_autorefresh_service import project_tree_autorefresh_service
from app.services.real_operator_rehearsal_service import real_operator_rehearsal_service


class InstallReadinessFinalGateService:
    """Final install gate for the real PC/APK operator flow.

    This is not another loose module. It checks the exact path the operator will
    use before first real install: Home, Modo Fácil, Teste geral, memory audit,
    rehearsal, APK/EXE artifacts, workflows, tree sync and safe autonomy rules.
    """

    REQUIRED_ROUTES = [
        "/api/god-mode-home/dashboard",
        "/api/home-operator-ux/panel",
        "/api/real-operator-rehearsal/run",
        "/api/andreos-memory-audit/audit",
        "/api/artifacts-center/dashboard",
        "/api/daily-command-router/route",
        "/api/install-readiness-final/status",
        "/api/install-readiness-final/check",
        "/api/install-readiness-final/package",
        "/app/home",
    ]

    REQUIRED_TREE_ENTRIES = [
        "install_readiness_final.py",
        "install_readiness_final_service.py",
        "install-readiness-final-gate.md",
        "prune-project-tree-sync-guard-validation.yml",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:400]}

    def build_check(
        self,
        tenant_id: str = "owner-andre",
        requested_project: str = "GOD_MODE",
        run_deep: bool = True,
    ) -> Dict[str, Any]:
        route_probe = self._route_probe()
        home = self._safe("home_dashboard", lambda: god_mode_home_service.build_dashboard(tenant_id=tenant_id))
        panel = self._safe("home_operator_ux_panel", lambda: home_operator_ux_service.build_panel(tenant_id=tenant_id))
        memory = self._safe("andreos_memory_audit", lambda: andreos_memory_audit_service.build_audit(run_rehearsal=run_deep))
        rehearsal = self._safe(
            "real_operator_rehearsal",
            lambda: real_operator_rehearsal_service.run(tenant_id=tenant_id, requested_project=requested_project),
        )
        artifacts = self._safe("artifacts_center", artifacts_center_service.build_dashboard)
        workflow_probe = self._workflow_probe()
        frontend_probe = self._frontend_probe()
        tree_probe = self._tree_probe()
        autonomy_probe = self._autonomy_probe(panel=panel, rehearsal=rehearsal)

        checks = [
            self._check("home_responds", "Home responde", home.get("ok") is True, home.get("operator_message")),
            self._check("easy_mode_exists", "Modo Fácil existe", panel.get("ok") is True and bool(panel.get("safe_buttons")), panel.get("headline")),
            self._check("general_test_exists_and_passes", "Teste geral existe e passa", self._general_test_ok(panel, rehearsal), {"button": self._button(panel, "general_test"), "score": rehearsal.get("score"), "status": rehearsal.get("status")}),
            self._check("andreos_memory_audit_passes", "AndreOS Memory Audit passa", memory.get("status") == "ready" and memory.get("score") == 100, {"status": memory.get("status"), "score": memory.get("score")}),
            self._check("real_operator_rehearsal_passes", "Real Operator Rehearsal passa", rehearsal.get("status") == "ready" and rehearsal.get("score") == 100, {"status": rehearsal.get("status"), "score": rehearsal.get("score")}),
            self._check("artifacts_center_points_to_apk_exe", "Artifacts Center aponta para APK/EXE", self._artifacts_ok(artifacts), {"status": artifacts.get("status"), "artifact_count": artifacts.get("artifact_count"), "artifacts": artifacts.get("artifacts", [])}),
            self._check("apk_exe_workflows_exist", "Workflows APK/EXE existem", workflow_probe.get("required_workflows_exist") is True, workflow_probe.get("workflows")),
            self._check("apk_artifact_not_placeholder", "APK artifact esperado não é placeholder", workflow_probe.get("apk", {}).get("ok") is True, workflow_probe.get("apk")),
            self._check("exe_artifact_not_placeholder", "EXE artifact esperado não é placeholder", workflow_probe.get("exe", {}).get("ok") is True, workflow_probe.get("exe")),
            self._check("project_tree_autorefresh_sees_new_files", "Project Tree Autorefresh vê ficheiros novos", tree_probe.get("ok") is True, tree_probe),
            self._check("no_secrets_in_memory", "Não há secrets graváveis na memória", self._memory_secret_guard_ok(memory), memory.get("secret_probe")),
            self._check("main_routes_exist", "Rotas principais existem", route_probe.get("ok") is True, route_probe),
            self._check("general_test_button_visible", "Botão Teste geral aparece no Modo Fácil", bool(self._button(panel, "general_test")), self._button(panel, "general_test")),
            self._check("home_result_card_ready", "Home consegue apresentar resultado em cartão", frontend_probe.get("result_card_ready") is True, frontend_probe),
            self._check("backend_autonomy_contract", "Backend continua sem APK até OK/credenciais/bloqueio/fim", autonomy_probe.get("ok") is True, autonomy_probe),
        ]
        failed = [check for check in checks if not check["ok"]]
        score = round((sum(1 for check in checks if check["ok"]) / len(checks)) * 100) if checks else 0
        status = "ready_to_install" if not failed else ("attention" if score >= 80 else "blocked")
        return {
            "ok": not failed,
            "mode": "install_readiness_final_gate",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": status,
            "score": score,
            "ready_to_install": not failed,
            "checks": checks,
            "failed_checks": failed,
            "summary": self._summary(status=status, score=score, failed=failed),
            "operator_next": self._operator_next(failed),
            "signals": {
                "home": self._home_summary(home),
                "easy_mode": self._panel_summary(panel),
                "memory": {"status": memory.get("status"), "score": memory.get("score")},
                "rehearsal": {"status": rehearsal.get("status"), "score": rehearsal.get("score")},
                "artifacts": {"status": artifacts.get("status"), "artifact_count": artifacts.get("artifact_count")},
                "routes": route_probe,
                "workflows": workflow_probe,
                "tree_autorefresh": tree_probe,
                "autonomy": autonomy_probe,
            },
        }

    def _route_probe(self) -> Dict[str, Any]:
        try:
            from main import app

            route_paths: Set[str] = {route.path for route in app.routes}
        except Exception as exc:
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:300], "missing_routes": self.REQUIRED_ROUTES}
        missing = sorted(set(self.REQUIRED_ROUTES) - route_paths)
        return {"ok": not missing, "required_routes": self.REQUIRED_ROUTES, "missing_routes": missing, "route_count": len(route_paths)}

    def _button(self, panel: Dict[str, Any], kind: str) -> Dict[str, Any] | None:
        for button in panel.get("safe_buttons", []) if isinstance(panel, dict) else []:
            if button.get("kind") == kind:
                return button
        return None

    def _general_test_ok(self, panel: Dict[str, Any], rehearsal: Dict[str, Any]) -> bool:
        button = self._button(panel, "general_test")
        return bool(
            button
            and button.get("label") == "Teste geral"
            and button.get("endpoint") == "/api/real-operator-rehearsal/run"
            and rehearsal.get("status") == "ready"
            and rehearsal.get("score") == 100
        )

    def _artifacts_ok(self, artifacts: Dict[str, Any]) -> bool:
        items = artifacts.get("artifacts", []) if isinstance(artifacts, dict) else []
        artifact_ids = {item.get("id") for item in items}
        expected_names = {item.get("expected_artifact_name") for item in items}
        expected_files = {item.get("expected_file") for item in items}
        return bool(
            artifacts.get("status") == "ready"
            and artifacts.get("artifact_count") == 2
            and {"apk", "exe"}.issubset(artifact_ids)
            and {"godmode-android-webview-apk", "godmode-windows-exe"}.issubset(expected_names)
            and {"GodModeMobile-debug.apk", "GodModeDesktop.exe"}.issubset(expected_files)
        )

    def _workflow_probe(self) -> Dict[str, Any]:
        specs = [
            {
                "id": "apk",
                "label": "Android APK workflow",
                "path": ".github/workflows/android-real-build-progressive.yml",
                "expected_artifact_name": "godmode-android-webview-apk",
                "expected_file": "GodModeMobile-debug.apk",
                "required_markers": ["gradle --no-daemon :app:assembleDebug", "GodModeMobile-debug.apk", "real_webview_shell_apk", "upload-artifact", "apk.stat().st_size > 1024"],
                "placeholder_markers": ["echo placeholder", "dummy artifact", "placeholder artifact", "fake apk"],
            },
            {
                "id": "exe",
                "label": "Windows EXE workflow",
                "path": ".github/workflows/windows-exe-real-build.yml",
                "expected_artifact_name": "godmode-windows-exe",
                "expected_file": "GodModeDesktop.exe",
                "required_markers": ["pyinstaller --clean --noconfirm desktop/GodModeDesktop.spec", "GodModeDesktop.exe", "desktop-installer-manifest.json", "upload-artifact"],
                "placeholder_markers": ["echo placeholder", "dummy artifact", "placeholder artifact", "fake exe"],
            },
        ]
        results: Dict[str, Any] = {"workflows": []}
        for spec in specs:
            path = Path(spec["path"])
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            lower = text.lower()
            missing_markers = [marker for marker in spec["required_markers"] if marker.lower() not in lower]
            placeholder_hits = [marker for marker in spec["placeholder_markers"] if marker in lower]
            item = {
                "id": spec["id"],
                "label": spec["label"],
                "path": spec["path"],
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
                "expected_artifact_name": spec["expected_artifact_name"],
                "expected_file": spec["expected_file"],
                "missing_markers": missing_markers,
                "placeholder_hits": placeholder_hits,
                "ok": path.exists() and not missing_markers and not placeholder_hits,
            }
            results[spec["id"]] = item
            results["workflows"].append(item)
        results["required_workflows_exist"] = all(item["exists"] for item in results["workflows"])
        results["ok"] = all(item["ok"] for item in results["workflows"])
        return results

    def _frontend_probe(self) -> Dict[str, Any]:
        path = Path("backend/app/routes/god_mode_home_frontend.py")
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        markers = [
            "renderResultCard",
            "resultCard",
            "Ver JSON",
            "runPayloadButton(endpoint,payload={})",
            "/api/install-readiness-final/check",
            "install_readiness_final",
            "Instalação final",
        ]
        missing = [marker for marker in markers if marker not in text]
        return {"ok": path.exists() and not missing, "result_card_ready": path.exists() and not missing, "path": str(path), "missing_markers": missing}

    def _tree_probe(self) -> Dict[str, Any]:
        generated_tree = project_tree_autorefresh_service.build_tree_text()
        missing = [entry for entry in self.REQUIRED_TREE_ENTRIES if entry not in generated_tree]
        return {
            "ok": not missing,
            "missing_entries": missing,
            "required_entries": self.REQUIRED_TREE_ENTRIES,
            "generated_line_count": len(generated_tree.splitlines()),
            "source": "Project Tree Autorefresh generated tree",
        }

    def _memory_secret_guard_ok(self, memory: Dict[str, Any]) -> bool:
        secret_probe = memory.get("secret_probe", {}) if isinstance(memory, dict) else {}
        return bool(secret_probe.get("blocked") is True and secret_probe.get("safe_write_ok") is True)

    def _autonomy_probe(self, panel: Dict[str, Any], rehearsal: Dict[str, Any]) -> Dict[str, Any]:
        rules_text = " ".join(panel.get("operator_rules", [])) if isinstance(panel, dict) else ""
        route_summary = rehearsal.get("flow", {}).get("route_result", {}) if isinstance(rehearsal, dict) else {}
        stop_reason_present = "autopilot_stop_reason" in route_summary
        contract = {
            "pc_is_brain": True,
            "apk_is_remote_control": True,
            "continues_after_apk_disconnect": True,
            "allowed_stop_reasons": ["operator_ok_required", "manual_credentials_required", "safe_blocked", "finished"],
            "preserve_local_state": ["data/", "memory/", ".env", "backend/.env"],
        }
        rule_ok = "backend continua" in rules_text.lower() and "terminar" in rules_text.lower()
        return {
            "ok": bool(rule_ok and stop_reason_present),
            "operator_rules_contain_contract": rule_ok,
            "rehearsal_has_autopilot_stop_reason": stop_reason_present,
            "observed_stop_reason": route_summary.get("autopilot_stop_reason"),
            "contract": contract,
        }

    def _check(self, check_id: str, label: str, ok: bool, detail: Any = "") -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok), "detail": detail}

    def _home_summary(self, home: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": home.get("ok"), "active_project": home.get("active_project"), "operator_message": home.get("operator_message"), "traffic_light": home.get("traffic_light")}

    def _panel_summary(self, panel: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": panel.get("ok"), "headline": panel.get("headline"), "safe_button_count": len(panel.get("safe_buttons", [])), "quick_command_count": len(panel.get("quick_commands", []))}

    def _summary(self, status: str, score: int, failed: List[Dict[str, Any]]) -> str:
        if not failed:
            return f"God Mode pronto para instalação real PC/APK · score {score}%"
        return f"God Mode ainda precisa corrigir {len(failed)} ponto(s) antes da instalação · status {status} · score {score}%"

    def _operator_next(self, failed: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not failed:
            return {"label": "Descarregar APK/EXE e seguir guia de instalação", "endpoint": "/api/artifacts-center/dashboard", "route": "/app/home"}
        first = failed[0]
        return {"label": f"Corrigir antes de instalar: {first['label']}", "endpoint": "/api/install-readiness-final/check", "route": "/app/home"}

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        check = self.build_check(tenant_id=tenant_id, run_deep=False)
        return {
            "ok": check["ok"],
            "mode": "install_readiness_final_status",
            "status": check["status"],
            "score": check["score"],
            "ready_to_install": check["ready_to_install"],
            "failed_count": len(check["failed_checks"]),
            "operator_next": check["operator_next"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "install_readiness_final_package",
            "package": {
                "status": self.get_status(tenant_id=tenant_id),
                "check": self.build_check(tenant_id=tenant_id, requested_project=requested_project, run_deep=True),
            },
        }


install_readiness_final_service = InstallReadinessFinalGateService()
