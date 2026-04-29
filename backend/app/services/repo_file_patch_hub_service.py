from __future__ import annotations

import difflib
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_context_router_service import memory_context_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PATCH_FILE = DATA_DIR / "repo_file_patch_hub.json"
PATCH_STORE = AtomicJsonStore(
    PATCH_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "preview_checkpoint_validate_then_apply_repo_file_patches",
        "plans": [],
        "previews": [],
        "checkpoints": [],
        "approvals": [],
        "runs": [],
    },
)


class RepoFilePatchHubService:
    """Safe repo/file patch orchestration.

    This hub prepares file/repo changes with preview, hashes, checkpoints,
    validation commands, approval contracts and rollback metadata. It does not
    silently mutate files. Real writes should be performed by an approved executor
    after this hub generates a precise patch plan.
    """

    APPROVAL_PHRASE = "APPLY REPO PATCH"
    MAX_FILE_BYTES = 400_000
    BLOCKED_PATH_PARTS = [
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
        ".git/",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_file_patch_policy",
            "approval_phrase": self.APPROVAL_PHRASE,
            "rules": [
                "gerar plano antes de mexer",
                "mostrar diff/preview por ficheiro",
                "criar checkpoint com hash original",
                "validar comandos antes de PR/build quando possível",
                "não alterar ficheiros sensíveis",
                "não escrever em .git",
                "não aplicar patches sem aprovação explícita",
            ],
            "blocked_path_parts": self.BLOCKED_PATH_PARTS,
            "real_write_executor": "future_or_existing_approved_executor",
        }

    def create_plan(
        self,
        project_id: str = "GOD_MODE",
        goal: str = "apply safe repo/file patch",
        target_repo: str = "AndreVazao/devops-god-mode",
        base_branch: str = "main",
        target_branch: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        validation_commands: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        normalized_files = [self._normalize_file_change(item) for item in (files or [])]
        blocked = [item for item in normalized_files if not item.get("safe_path")]
        safe_files = [item for item in normalized_files if item.get("safe_path")]
        plan = {
            "plan_id": f"repo-patch-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": self._normalize_project(project_id),
            "goal": goal,
            "target_repo": target_repo,
            "base_branch": base_branch,
            "target_branch": target_branch or f"godmode-auto/{uuid4().hex[:8]}",
            "safe_files": safe_files,
            "blocked_files": blocked,
            "file_count": len(normalized_files),
            "safe_file_count": len(safe_files),
            "blocked_file_count": len(blocked),
            "validation_commands": validation_commands or self._default_validation_commands(safe_files),
            "approval_required": True,
            "approval_phrase": self.APPROVAL_PHRASE,
            "status": "blocked_paths_present" if blocked else "ready_for_preview",
        }
        self._store("plans", plan)
        memory_context_router_service.prepare_project_context(
            project_id=plan["project_id"],
            source="repo_file_patch_plan",
            idea=f"Patch plan {plan['plan_id']}: {goal}",
            max_chars=4000,
        )
        return {"ok": True, "mode": "repo_file_patch_plan", "plan": plan}

    def _normalize_file_change(self, item: Dict[str, Any]) -> Dict[str, Any]:
        path = str(item.get("path") or "").strip().replace("\\", "/")
        old_content = item.get("old_content")
        new_content = item.get("new_content")
        change_type = item.get("change_type") or ("update" if old_content is not None else "create")
        safe = self._is_safe_path(path)
        if isinstance(new_content, str) and len(new_content.encode("utf-8")) > self.MAX_FILE_BYTES:
            safe = False
        return {
            "file_change_id": f"file-change-{uuid4().hex[:10]}",
            "path": path,
            "change_type": change_type,
            "safe_path": safe,
            "unsafe_reason": None if safe else self._unsafe_reason(path, new_content),
            "old_sha256": self._sha(old_content) if isinstance(old_content, str) else None,
            "new_sha256": self._sha(new_content) if isinstance(new_content, str) else None,
            "old_size": len(old_content.encode("utf-8")) if isinstance(old_content, str) else 0,
            "new_size": len(new_content.encode("utf-8")) if isinstance(new_content, str) else 0,
            "old_content": old_content,
            "new_content": new_content,
            "summary": item.get("summary") or f"{change_type} {path}",
        }

    def _is_safe_path(self, path: str) -> bool:
        if not path or path.startswith("/") or ".." in Path(path).parts:
            return False
        lowered = path.lower()
        return not any(part in lowered for part in self.BLOCKED_PATH_PARTS)

    def _unsafe_reason(self, path: str, content: Any) -> str:
        if not path:
            return "empty_path"
        if path.startswith("/") or ".." in Path(path).parts:
            return "unsafe_path_traversal"
        lowered = path.lower()
        if any(part in lowered for part in self.BLOCKED_PATH_PARTS):
            return "sensitive_or_blocked_path"
        if isinstance(content, str) and len(content.encode("utf-8")) > self.MAX_FILE_BYTES:
            return "file_too_large_for_safe_patch_preview"
        return "unknown_unsafe_path"

    def _sha(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _default_validation_commands(self, files: List[Dict[str, Any]]) -> List[str]:
        paths = " ".join(item.get("path", "") for item in files).lower()
        commands: List[str] = []
        if "backend/" in paths or ".py" in paths:
            commands.append("python -m compileall backend")
        if "frontend/" in paths or ".ts" in paths or ".tsx" in paths or ".js" in paths:
            commands.append("npm test -- --runInBand")
        if ".md" in paths:
            commands.append("documentation review")
        return commands or ["universal backend import and route test"]

    def preview(self, plan_id: str) -> Dict[str, Any]:
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "repo_file_patch_preview", "error": "plan_not_found"}
        previews = []
        for item in plan.get("safe_files", []):
            old = item.get("old_content") or ""
            new = item.get("new_content") or ""
            diff = "".join(difflib.unified_diff(
                old.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=f"a/{item.get('path')}",
                tofile=f"b/{item.get('path')}",
            ))
            previews.append({
                "file_change_id": item.get("file_change_id"),
                "path": item.get("path"),
                "change_type": item.get("change_type"),
                "old_sha256": item.get("old_sha256"),
                "new_sha256": item.get("new_sha256"),
                "diff": diff[-20000:],
                "diff_truncated": len(diff) > 20000,
            })
        preview = {
            "preview_id": f"repo-patch-preview-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "target_repo": plan.get("target_repo"),
            "target_branch": plan.get("target_branch"),
            "file_previews": previews,
            "blocked_files": plan.get("blocked_files", []),
            "validation_commands": plan.get("validation_commands", []),
            "approval_phrase": self.APPROVAL_PHRASE,
            "status": "ready_for_approval" if not plan.get("blocked_files") else "needs_review_blocked_files",
        }
        self._store("previews", preview)
        return {"ok": True, "mode": "repo_file_patch_preview", "preview": preview}

    def checkpoint(self, plan_id: str) -> Dict[str, Any]:
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "repo_file_patch_checkpoint", "error": "plan_not_found"}
        checkpoint = {
            "checkpoint_id": f"repo-patch-checkpoint-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "target_repo": plan.get("target_repo"),
            "base_branch": plan.get("base_branch"),
            "target_branch": plan.get("target_branch"),
            "files": [
                {
                    "path": item.get("path"),
                    "old_sha256": item.get("old_sha256"),
                    "old_size": item.get("old_size"),
                    "rollback_content_available": item.get("old_content") is not None,
                    "old_content": item.get("old_content"),
                }
                for item in plan.get("safe_files", [])
            ],
            "rollback_policy": "restore old_content by exact path if apply fails or operator requests rollback",
        }
        self._store("checkpoints", checkpoint)
        return {"ok": True, "mode": "repo_file_patch_checkpoint", "checkpoint": checkpoint}

    def approve(self, plan_id: str, approval_phrase: str) -> Dict[str, Any]:
        if approval_phrase != self.APPROVAL_PHRASE:
            return {"ok": False, "mode": "repo_file_patch_approval", "error": "approval_phrase_required", "required_phrase": self.APPROVAL_PHRASE}
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "repo_file_patch_approval", "error": "plan_not_found"}
        if plan.get("blocked_files"):
            return {"ok": False, "mode": "repo_file_patch_approval", "error": "blocked_files_present", "blocked_files": plan.get("blocked_files")}
        preview = self.preview(plan_id).get("preview")
        checkpoint = self.checkpoint(plan_id).get("checkpoint")
        approval = {
            "approval_id": f"repo-patch-approval-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "preview_id": (preview or {}).get("preview_id"),
            "checkpoint_id": (checkpoint or {}).get("checkpoint_id"),
            "approval_phrase": self.APPROVAL_PHRASE,
            "status": "approved_for_executor",
            "executor_contract": {
                "write_target_branch": plan.get("target_branch"),
                "apply_exact_files_only": True,
                "run_validation_commands": plan.get("validation_commands", []),
                "open_pull_request": True,
                "rollback_on_failure": True,
            },
        }
        self._store("approvals", approval)
        return {"ok": True, "mode": "repo_file_patch_approval", "approval": approval}

    def record_run(
        self,
        plan_id: str,
        status: str = "completed",
        pr_url: Optional[str] = None,
        validation_result: Optional[Dict[str, Any]] = None,
        rollback_available: bool = True,
    ) -> Dict[str, Any]:
        run = {
            "run_id": f"repo-patch-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "status": status,
            "pr_url": pr_url,
            "validation_result": validation_result or {},
            "rollback_available": rollback_available,
        }
        self._store("runs", run)
        return {"ok": True, "mode": "repo_file_patch_run_recorded", "run": run}

    def _find(self, key: str, value: str, id_key: str) -> Optional[Dict[str, Any]]:
        items = PATCH_STORE.load().get(key, [])
        return next((item for item in items if item.get(id_key) == value), None)

    def _normalize_project(self, project_id: str) -> str:
        return (project_id or "GOD_MODE").strip().upper().replace("-", "_").replace(" ", "_")

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-100:]
            return state
        PATCH_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = PATCH_STORE.load()
        return {
            "ok": True,
            "mode": "repo_file_patch_latest",
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_preview": (state.get("previews") or [None])[-1],
            "latest_checkpoint": (state.get("checkpoints") or [None])[-1],
            "latest_approval": (state.get("approvals") or [None])[-1],
            "latest_run": (state.get("runs") or [None])[-1],
            "plan_count": len(state.get("plans") or []),
            "approval_count": len(state.get("approvals") or []),
            "run_count": len(state.get("runs") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_file_patch_panel",
            "headline": "Patches reais com preview, checkpoint, validação e PR",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "plan", "label": "Criar plano patch", "endpoint": "/api/repo-file-patch/plan", "priority": "critical"},
                {"id": "preview", "label": "Preview diff", "endpoint": "/api/repo-file-patch/preview", "priority": "critical"},
                {"id": "checkpoint", "label": "Checkpoint", "endpoint": "/api/repo-file-patch/checkpoint", "priority": "high"},
                {"id": "approve", "label": "Aprovar patch", "endpoint": "/api/repo-file-patch/approve", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "repo_file_patch_status",
            "plan_count": latest.get("plan_count", 0),
            "approval_count": latest.get("approval_count", 0),
            "run_count": latest.get("run_count", 0),
            "approval_phrase": self.APPROVAL_PHRASE,
            "real_write_guarded": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "repo_file_patch_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


repo_file_patch_hub_service = RepoFilePatchHubService()
