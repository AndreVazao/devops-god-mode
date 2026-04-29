from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
RESTORE_DIR = DATA_DIR / "restore"
PRE_RESTORE_BACKUP_DIR = RESTORE_DIR / "pre_restore_backups"
RESTORE_FILE = DATA_DIR / "restore_approved_runner.json"
RESTORE_STORE = AtomicJsonStore(
    RESTORE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "preview_approve_backup_restore_rollback",
        "previews": [],
        "restore_runs": [],
        "rollback_runs": [],
    },
)


class RestoreApprovedRunnerService:
    """Approved restore runner for portable God Mode backups.

    Restore is intentionally staged and approval-gated:
    1. Inspect ZIP.
    2. Validate manifest and safe paths.
    3. Show conflicts.
    4. Create pre-restore backup for files that would be overwritten.
    5. Apply selected files only after explicit approval phrase.
    6. Store rollback plan.
    """

    REQUIRED_APPROVAL_PHRASE = "RESTORE GOD MODE"
    MAX_PREVIEW_FILES = 5000
    ALLOWED_TOP_LEVEL = {
        "memory",
        "data",
        "docs",
        "frontend",
        "desktop",
        "scripts",
        "README.md",
        "PROJECT_TREE.txt",
        "BACKUP_MANIFEST.json",
        "RESTORE_README.txt",
    }
    SENSITIVE_NAME_PARTS = [
        ".env",
        "secret",
        "token",
        "password",
        "cookie",
        "credential",
        "authorization",
        "bearer",
        "api_key",
        "apikey",
        "private_key",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _repo_root(self) -> Path:
        return Path.cwd()

    def _normalize_zip_name(self, name: str) -> Optional[Path]:
        if not name or name.endswith("/"):
            return None
        if name.startswith("/") or name.startswith("\\"):
            return None
        cleaned = Path(name.replace("\\", "/"))
        if any(part in {"..", ""} for part in cleaned.parts):
            return None
        if cleaned.parts and cleaned.parts[0] not in self.ALLOWED_TOP_LEVEL:
            return None
        return cleaned

    def _is_sensitive(self, path: Path) -> bool:
        lowered = str(path).lower().replace("\\", "/")
        return any(part in lowered for part in self.SENSITIVE_NAME_PARTS)

    def _load_manifest(self, zf: zipfile.ZipFile) -> Dict[str, Any]:
        if "BACKUP_MANIFEST.json" not in zf.namelist():
            return {}
        try:
            return json.loads(zf.read("BACKUP_MANIFEST.json").decode("utf-8"))
        except Exception as exc:
            return {"manifest_error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def preview(self, backup_path: str, restore_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        source = Path(backup_path)
        if not source.exists() or not source.is_file():
            return {"ok": False, "mode": "restore_approved_preview", "error": "backup_not_found", "backup_path": backup_path}
        preview_id = f"restore-preview-{uuid4().hex[:12]}"
        root = self._repo_root()
        filters = [item.strip().replace("\\", "/") for item in (restore_filter or []) if item.strip()]
        safe_files: List[Dict[str, Any]] = []
        blocked_files: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        manifest: Dict[str, Any] = {}
        try:
            with zipfile.ZipFile(source, "r") as zf:
                manifest = self._load_manifest(zf)
                names = zf.namelist()
                if len(names) > self.MAX_PREVIEW_FILES:
                    return {"ok": False, "mode": "restore_approved_preview", "error": "too_many_files", "count": len(names)}
                for name in names:
                    rel = self._normalize_zip_name(name)
                    if rel is None:
                        blocked_files.append({"name": name, "reason": "unsafe_or_not_allowlisted_path"})
                        continue
                    if filters and not any(str(rel).replace("\\", "/").startswith(prefix) for prefix in filters):
                        continue
                    if self._is_sensitive(rel):
                        blocked_files.append({"name": name, "reason": "sensitive_path_excluded"})
                        continue
                    target = root / rel
                    info = zf.getinfo(name)
                    file_item = {
                        "zip_name": name,
                        "relative_path": str(rel).replace("\\", "/"),
                        "target_path": str(target),
                        "size": info.file_size,
                        "exists": target.exists(),
                    }
                    safe_files.append(file_item)
                    if target.exists():
                        conflicts.append(file_item)
        except zipfile.BadZipFile:
            return {"ok": False, "mode": "restore_approved_preview", "error": "bad_zip_file", "backup_path": backup_path}

        preview = {
            "preview_id": preview_id,
            "created_at": self._now(),
            "backup_path": str(source),
            "manifest": manifest,
            "safe_file_count": len(safe_files),
            "blocked_file_count": len(blocked_files),
            "conflict_count": len(conflicts),
            "safe_files": safe_files[:1000],
            "blocked_files": blocked_files[:1000],
            "conflicts": conflicts[:1000],
            "restore_filter": filters,
            "requires_approval_phrase": self.REQUIRED_APPROVAL_PHRASE,
            "will_create_pre_restore_backup": bool(conflicts),
            "will_not_restore_sensitive_paths": True,
            "will_not_restore_unsafe_paths": True,
        }
        self._store_preview(preview)
        return {"ok": True, "mode": "restore_approved_preview", "preview": preview}

    def restore(
        self,
        backup_path: str,
        approval_phrase: str,
        restore_filter: Optional[List[str]] = None,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        if approval_phrase != self.REQUIRED_APPROVAL_PHRASE:
            return {
                "ok": False,
                "mode": "restore_approved_run",
                "error": "approval_phrase_required",
                "required_phrase": self.REQUIRED_APPROVAL_PHRASE,
            }
        preview_result = self.preview(backup_path=backup_path, restore_filter=restore_filter)
        if not preview_result.get("ok"):
            return preview_result
        preview = preview_result.get("preview") or {}
        if preview.get("conflict_count", 0) > 0 and not overwrite:
            return {
                "ok": False,
                "mode": "restore_approved_run",
                "error": "conflicts_require_overwrite_true",
                "preview": preview,
            }

        source = Path(backup_path)
        root = self._repo_root()
        run_id = f"restore-run-{uuid4().hex[:12]}"
        pre_backup = self._create_pre_restore_backup(preview, run_id)
        restored: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        try:
            with zipfile.ZipFile(source, "r") as zf:
                for item in preview.get("safe_files", []):
                    rel = Path(item["relative_path"])
                    target = root / rel
                    try:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(item["zip_name"], "r") as src, target.open("wb") as dst:
                            shutil.copyfileobj(src, dst)
                        restored.append({"relative_path": item["relative_path"], "target_path": str(target), "overwrote": item.get("exists", False)})
                    except Exception as exc:
                        errors.append({"relative_path": item.get("relative_path"), "error": exc.__class__.__name__, "detail": str(exc)[:300]})
        except Exception as exc:
            errors.append({"error": exc.__class__.__name__, "detail": str(exc)[:500]})

        rollback_plan = {
            "rollback_id": f"rollback-{uuid4().hex[:12]}",
            "pre_restore_backup_path": pre_backup.get("zip_path"),
            "restored_paths": [item["relative_path"] for item in restored],
            "created_at": self._now(),
        }
        run = {
            "run_id": run_id,
            "created_at": self._now(),
            "backup_path": str(source),
            "preview_id": preview.get("preview_id"),
            "restored_count": len(restored),
            "error_count": len(errors),
            "restored": restored[:1000],
            "errors": errors,
            "pre_restore_backup": pre_backup,
            "rollback_plan": rollback_plan,
            "status": "completed_with_errors" if errors else "completed",
        }
        self._store_restore_run(run)
        return {"ok": len(errors) == 0, "mode": "restore_approved_run", "run": run}

    def _create_pre_restore_backup(self, preview: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        PRE_RESTORE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        root = self._repo_root()
        zip_path = PRE_RESTORE_BACKUP_DIR / f"{run_id}-pre-restore.zip"
        backed_up: List[str] = []
        skipped: List[str] = []
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in preview.get("conflicts", []):
                rel = Path(item["relative_path"])
                target = root / rel
                if target.exists() and target.is_file() and not self._is_sensitive(rel):
                    try:
                        zf.write(target, arcname=str(rel).replace("\\", "/"))
                        backed_up.append(str(rel).replace("\\", "/"))
                    except Exception:
                        skipped.append(str(rel).replace("\\", "/"))
            zf.writestr("PRE_RESTORE_MANIFEST.json", json.dumps({
                "run_id": run_id,
                "created_at": self._now(),
                "backed_up": backed_up,
                "skipped": skipped,
            }, indent=2, ensure_ascii=False))
        return {"zip_path": str(zip_path), "backed_up_count": len(backed_up), "skipped_count": len(skipped), "backed_up": backed_up[:1000], "skipped": skipped[:1000]}

    def rollback(self, pre_restore_backup_path: str, approval_phrase: str) -> Dict[str, Any]:
        if approval_phrase != self.REQUIRED_APPROVAL_PHRASE:
            return {"ok": False, "mode": "restore_approved_rollback", "error": "approval_phrase_required", "required_phrase": self.REQUIRED_APPROVAL_PHRASE}
        source = Path(pre_restore_backup_path)
        if not source.exists() or not source.is_file():
            return {"ok": False, "mode": "restore_approved_rollback", "error": "pre_restore_backup_not_found", "path": pre_restore_backup_path}
        root = self._repo_root()
        restored: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        try:
            with zipfile.ZipFile(source, "r") as zf:
                for name in zf.namelist():
                    rel = self._normalize_zip_name(name)
                    if rel is None or name == "PRE_RESTORE_MANIFEST.json" or self._is_sensitive(rel):
                        continue
                    target = root / rel
                    try:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(name, "r") as src, target.open("wb") as dst:
                            shutil.copyfileobj(src, dst)
                        restored.append({"relative_path": str(rel).replace("\\", "/"), "target_path": str(target)})
                    except Exception as exc:
                        errors.append({"relative_path": str(rel), "error": exc.__class__.__name__, "detail": str(exc)[:300]})
        except Exception as exc:
            errors.append({"error": exc.__class__.__name__, "detail": str(exc)[:500]})
        rollback_run = {
            "rollback_run_id": f"rollback-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pre_restore_backup_path": str(source),
            "restored_count": len(restored),
            "error_count": len(errors),
            "restored": restored[:1000],
            "errors": errors,
            "status": "completed_with_errors" if errors else "completed",
        }
        self._store_rollback_run(rollback_run)
        return {"ok": len(errors) == 0, "mode": "restore_approved_rollback", "rollback": rollback_run}

    def _store_preview(self, preview: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("previews", [])
            state["previews"].append(preview)
            state["previews"] = state["previews"][-100:]
            return state
        RESTORE_STORE.update(mutate)

    def _store_restore_run(self, run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("restore_runs", [])
            state["restore_runs"].append(run)
            state["restore_runs"] = state["restore_runs"][-100:]
            return state
        RESTORE_STORE.update(mutate)

    def _store_rollback_run(self, rollback_run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("rollback_runs", [])
            state["rollback_runs"].append(rollback_run)
            state["rollback_runs"] = state["rollback_runs"][-100:]
            return state
        RESTORE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = RESTORE_STORE.load()
        previews = state.get("previews") or []
        runs = state.get("restore_runs") or []
        rollbacks = state.get("rollback_runs") or []
        return {
            "ok": True,
            "mode": "restore_approved_latest",
            "latest_preview": previews[-1] if previews else None,
            "latest_restore_run": runs[-1] if runs else None,
            "latest_rollback_run": rollbacks[-1] if rollbacks else None,
            "preview_count": len(previews),
            "restore_run_count": len(runs),
            "rollback_run_count": len(rollbacks),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "restore_approved_panel",
            "headline": "Restaurar backup God Mode com aprovação",
            "status": self.get_status(),
            "latest": self.latest(),
            "required_phrase": self.REQUIRED_APPROVAL_PHRASE,
            "safe_buttons": [
                {"id": "preview", "label": "Preview restore", "endpoint": "/api/restore-approved/preview", "priority": "critical"},
                {"id": "restore", "label": "Restaurar aprovado", "endpoint": "/api/restore-approved/run", "priority": "critical"},
                {"id": "rollback", "label": "Rollback", "endpoint": "/api/restore-approved/rollback", "priority": "high"},
                {"id": "latest", "label": "Último estado", "endpoint": "/api/restore-approved/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "restore_approved_status",
            "preview_count": latest.get("preview_count", 0),
            "restore_run_count": latest.get("restore_run_count", 0),
            "rollback_run_count": latest.get("rollback_run_count", 0),
            "approval_required": True,
            "required_phrase": self.REQUIRED_APPROVAL_PHRASE,
            "path_traversal_guard": True,
            "sensitive_path_guard": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "restore_approved_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


restore_approved_runner_service = RestoreApprovedRunnerService()
