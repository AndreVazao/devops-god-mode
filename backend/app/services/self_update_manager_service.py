from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.real_install_smoke_test_service import real_install_smoke_test_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
UPDATE_FILE = DATA_DIR / "self_update_manager.json"
UPDATE_STORE = AtomicJsonStore(
    UPDATE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "backup_manifest_smoke_test_then_swap_with_rollback",
        "plans": [],
        "backups": [],
        "approvals": [],
        "runs": [],
        "rollbacks": [],
    },
)


class SelfUpdateManagerService:
    """Self-update manager for God Mode.

    This service defines a safe contract for updating God Mode itself. It does
    not blindly overwrite the running system. It creates a plan, requires backup,
    records artifact metadata, runs smoke tests and keeps rollback information.
    """

    APPROVAL_PHRASE = "UPDATE GOD MODE"
    ROLLBACK_PHRASE = "ROLLBACK GOD MODE"
    PRESERVE_PATHS = ["data/", "memory/", ".env", "backend/.env"]
    CRITICAL_ARTIFACTS = [
        {"id": "windows_exe", "name": "GodModeDesktop.exe", "workflow": "windows-exe-real-build.yml"},
        {"id": "android_apk", "name": "GodModeMobile-debug.apk", "workflow": "android-real-build-progressive.yml"},
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "self_update_policy",
            "approval_phrase": self.APPROVAL_PHRASE,
            "rollback_phrase": self.ROLLBACK_PHRASE,
            "preserve_paths": self.PRESERVE_PATHS,
            "rules": [
                "nunca apagar data/ memory/ .env backend/.env",
                "criar plano antes de update",
                "criar backup antes de trocar binários/bundle",
                "validar artifacts esperados",
                "rodar smoke test depois do update",
                "rollback se smoke test falhar",
                "pedir aprovação para update completo",
                "updates pequenos podem ser preparados automaticamente mas troca real fica gated",
            ],
            "artifact_policy": {
                "exe_updates_replace_pc_launcher": True,
                "apk_updates_require_new_apk_install_when_shell_changes": True,
                "backend_only_updates_do_not_always_require_apk_reinstall": True,
            },
        }

    def create_plan(
        self,
        current_version: str = "unknown",
        target_version: str = "latest",
        target_commit: str = "unknown",
        update_kind: str = "full_bundle",
        artifact_manifest: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        manifest = artifact_manifest or self._default_manifest(target_commit=target_commit, target_version=target_version)
        plan = {
            "plan_id": f"self-update-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "current_version": current_version,
            "target_version": target_version,
            "target_commit": target_commit,
            "update_kind": update_kind,
            "artifact_manifest": manifest,
            "preserve_paths": self.PRESERVE_PATHS,
            "steps": self._steps(update_kind),
            "requires_operator_approval": update_kind in {"full_bundle", "exe", "apk", "db_migration"},
            "approval_phrase": self.APPROVAL_PHRASE,
            "smoke_test_endpoint": "/api/real-install-smoke-test/ci-safe",
            "rollback_available": True,
            "status": "planned",
        }
        self._store("plans", plan)
        return {"ok": True, "mode": "self_update_plan", "plan": plan}

    def _default_manifest(self, target_commit: str, target_version: str) -> Dict[str, Any]:
        return {
            "manifest_id": f"artifact-manifest-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "target_version": target_version,
            "target_commit": target_commit,
            "artifacts": self.CRITICAL_ARTIFACTS,
            "source": "github_actions_artifacts",
        }

    def _steps(self, update_kind: str) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "verificar versão atual", "safe": True},
            {"step": 2, "label": "validar manifesto/artifacts", "safe": True},
            {"step": 3, "label": "criar backup local", "safe": True},
            {"step": 4, "label": "preservar data/memory/env", "safe": True},
            {"step": 5, "label": f"preparar update {update_kind}", "safe": True},
            {"step": 6, "label": "pedir aprovação se necessário", "safe": True},
            {"step": 7, "label": "trocar bundle/binários", "safe": False},
            {"step": 8, "label": "reiniciar backend/launcher", "safe": False},
            {"step": 9, "label": "rodar smoke test", "safe": True},
            {"step": 10, "label": "confirmar update ou rollback", "safe": True},
        ]

    def create_backup_record(self, plan_id: str, backup_path: Optional[str] = None) -> Dict[str, Any]:
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "self_update_backup", "error": "plan_not_found"}
        backup = {
            "backup_id": f"self-update-backup-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "backup_path": backup_path or f"data/backups/self_update/{plan_id}.zip",
            "preserve_paths": self.PRESERVE_PATHS,
            "status": "recorded",
            "sha256_hint": self._sha(f"{plan_id}:{backup_path or ''}"),
        }
        self._store("backups", backup)
        return {"ok": True, "mode": "self_update_backup", "backup": backup}

    def approve(self, plan_id: str, approval_phrase: str) -> Dict[str, Any]:
        if approval_phrase != self.APPROVAL_PHRASE:
            return {"ok": False, "mode": "self_update_approval", "error": "approval_phrase_required", "required_phrase": self.APPROVAL_PHRASE}
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "self_update_approval", "error": "plan_not_found"}
        backup = self._latest_for_plan("backups", plan_id)
        if not backup:
            return {"ok": False, "mode": "self_update_approval", "error": "backup_required_before_approval"}
        approval = {
            "approval_id": f"self-update-approval-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "backup_id": backup.get("backup_id"),
            "approval_phrase": self.APPROVAL_PHRASE,
            "status": "approved_for_update_executor",
            "executor_contract": {
                "preserve_paths": self.PRESERVE_PATHS,
                "apply_update_kind": plan.get("update_kind"),
                "target_version": plan.get("target_version"),
                "target_commit": plan.get("target_commit"),
                "run_smoke_test_after_apply": True,
                "rollback_on_smoke_fail": True,
            },
        }
        self._store("approvals", approval)
        return {"ok": True, "mode": "self_update_approval", "approval": approval}

    def record_run(
        self,
        plan_id: str,
        status: str = "prepared",
        applied_version: Optional[str] = None,
        smoke_test_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "self_update_run", "error": "plan_not_found"}
        smoke = smoke_test_result or real_install_smoke_test_service.run_ci_safe()
        ok = bool(smoke.get("ok", False)) and status in {"prepared", "applied", "completed"}
        run = {
            "run_id": f"self-update-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "status": status,
            "applied_version": applied_version or plan.get("target_version"),
            "smoke_test_result": smoke,
            "ok": ok,
            "rollback_recommended": not ok,
        }
        self._store("runs", run)
        return {"ok": True, "mode": "self_update_run", "run": run}

    def rollback_plan(self, plan_id: str, rollback_phrase: str = "") -> Dict[str, Any]:
        if rollback_phrase and rollback_phrase != self.ROLLBACK_PHRASE:
            return {"ok": False, "mode": "self_update_rollback", "error": "rollback_phrase_invalid", "required_phrase": self.ROLLBACK_PHRASE}
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "self_update_rollback", "error": "plan_not_found"}
        backup = self._latest_for_plan("backups", plan_id)
        rollback = {
            "rollback_id": f"self-update-rollback-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "backup_id": (backup or {}).get("backup_id"),
            "backup_path": (backup or {}).get("backup_path"),
            "status": "ready_for_rollback" if backup else "missing_backup",
            "requires_phrase": self.ROLLBACK_PHRASE,
            "steps": [
                "parar backend/launcher novo",
                "restaurar backup preservado",
                "reiniciar versão anterior",
                "rodar smoke test",
                "registar resultado",
            ],
        }
        self._store("rollbacks", rollback)
        return {"ok": bool(backup), "mode": "self_update_rollback", "rollback": rollback}

    def _sha(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _find(self, key: str, value: str, id_key: str) -> Optional[Dict[str, Any]]:
        items = UPDATE_STORE.load().get(key, [])
        return next((item for item in items if item.get(id_key) == value), None)

    def _latest_for_plan(self, key: str, plan_id: str) -> Optional[Dict[str, Any]]:
        items = [item for item in UPDATE_STORE.load().get(key, []) if item.get("plan_id") == plan_id]
        return items[-1] if items else None

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        UPDATE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = UPDATE_STORE.load()
        return {
            "ok": True,
            "mode": "self_update_latest",
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_backup": (state.get("backups") or [None])[-1],
            "latest_approval": (state.get("approvals") or [None])[-1],
            "latest_run": (state.get("runs") or [None])[-1],
            "latest_rollback": (state.get("rollbacks") or [None])[-1],
            "plan_count": len(state.get("plans") or []),
            "run_count": len(state.get("runs") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "self_update_panel",
            "headline": "Atualização segura do God Mode",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "plan", "label": "Plano update", "endpoint": "/api/self-update/plan", "priority": "critical"},
                {"id": "backup", "label": "Registar backup", "endpoint": "/api/self-update/backup", "priority": "critical"},
                {"id": "approve", "label": "Aprovar update", "endpoint": "/api/self-update/approve", "priority": "critical"},
                {"id": "smoke", "label": "Smoke test", "endpoint": "/api/real-install-smoke-test/ci-safe", "priority": "high"},
                {"id": "rollback", "label": "Rollback", "endpoint": "/api/self-update/rollback", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "self_update_status",
            "plan_count": latest.get("plan_count", 0),
            "run_count": latest.get("run_count", 0),
            "approval_phrase": self.APPROVAL_PHRASE,
            "rollback_phrase": self.ROLLBACK_PHRASE,
            "preserve_paths": self.PRESERVE_PATHS,
            "requires_backup_before_update": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "self_update_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


self_update_manager_service = SelfUpdateManagerService()
