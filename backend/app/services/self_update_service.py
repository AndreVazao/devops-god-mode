from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
UPDATE_STATE_FILE = DATA_DIR / "self_update_state.json"
UPDATE_STORE = AtomicJsonStore(
    UPDATE_STATE_FILE,
    default_factory=lambda: {"plans": [], "runs": [], "backups": []},
)

DEFAULT_PRESERVE_PATHS = [
    "data",
    "memory",
    ".env",
    "backend/.env",
    "frontend/mobile-shell/backend-presets.example.json",
]
DEFAULT_MANAGED_PATHS = [
    "backend",
    "frontend",
    "desktop",
    "scripts",
    "docs",
    ".github/workflows",
    "README.md",
    "PROJECT_TREE.txt",
]


class SelfUpdateService:
    """Plans and runs safe local updates while preserving God Mode memory/state."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "self_update_status",
            "status": "self_update_ready",
            "store_file": str(UPDATE_STATE_FILE),
            "atomic_store_enabled": True,
            "platform": platform.platform(),
            "git_available": self._git_available(),
            "plan_count": len(store.get("plans", [])),
            "run_count": len(store.get("runs", [])),
            "backup_count": len(store.get("backups", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"plans": [], "runs": [], "backups": []}
        store.setdefault("plans", [])
        store.setdefault("runs", [])
        store.setdefault("backups", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(UPDATE_STORE.load())

    def _git_available(self) -> bool:
        return shutil.which("git") is not None

    def _run_command(self, args: List[str], timeout: int = 60) -> Dict[str, Any]:
        try:
            completed = subprocess.run(args, cwd=Path("."), capture_output=True, text=True, timeout=timeout, check=False)
            return {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-5000:],
                "stderr": completed.stderr[-5000:],
                "args": args,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc), "args": args}

    def current_git_state(self) -> Dict[str, Any]:
        if not self._git_available() or not (Path(".git").exists() or Path("../.git").exists()):
            return {"ok": False, "error": "git_not_available_or_not_a_repo"}
        branch = self._run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        commit = self._run_command(["git", "rev-parse", "HEAD"])
        status = self._run_command(["git", "status", "--porcelain"])
        remote = self._run_command(["git", "remote", "-v"])
        return {
            "ok": branch.get("ok") and commit.get("ok") and status.get("ok"),
            "branch": branch.get("stdout", "").strip(),
            "commit": commit.get("stdout", "").strip(),
            "dirty": bool(status.get("stdout", "").strip()),
            "status_porcelain": status.get("stdout", ""),
            "remote": remote.get("stdout", ""),
        }

    def create_update_plan(self, channel: str = "main", strategy: str = "git_pull_then_rebuild") -> Dict[str, Any]:
        git_state = self.current_git_state()
        plan = {
            "plan_id": f"update-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "channel": channel,
            "strategy": strategy,
            "status": "planned",
            "git_state": git_state,
            "preserve_paths": DEFAULT_PRESERVE_PATHS,
            "managed_paths": DEFAULT_MANAGED_PATHS,
            "steps": [
                "Verificar estado Git e ficheiros locais modificados.",
                "Criar backup de data/ e memory/ antes de atualizar.",
                "Fazer fetch/pull do canal configurado.",
                "Reinstalar dependências se necessário.",
                "Recriar EXE/APK quando o build muda.",
                "Restaurar/preservar memória e dados locais.",
                "Executar health check e validações rápidas.",
            ],
            "rules": [
                "Nunca apagar data/ nem memory/ durante update.",
                "Nunca sobrescrever .env ou credenciais locais.",
                "Se houver alterações locais não commitadas, parar e pedir aprovação.",
                "Rollback deve usar backup local do update.",
            ],
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["plans"].append(plan)
            store["plans"] = store["plans"][-100:]
            return store

        UPDATE_STORE.update(mutate)
        return {"ok": True, "mode": "self_update_plan", "plan": plan}

    def create_backup_manifest(self) -> Dict[str, Any]:
        backup_id = f"backup-{uuid4().hex[:12]}"
        existing = [path for path in DEFAULT_PRESERVE_PATHS if Path(path).exists()]
        manifest = {
            "backup_id": backup_id,
            "created_at": self._now(),
            "status": "manifest_only",
            "preserved_existing_paths": existing,
            "recommended_backup_dir": f"backups/{backup_id}",
            "note": "Manifest criado sem copiar ficheiros. Cópia real deve correr no PC local antes do update.",
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["backups"].append(manifest)
            store["backups"] = store["backups"][-100:]
            return store

        UPDATE_STORE.update(mutate)
        return {"ok": True, "mode": "self_update_backup_manifest", "backup": manifest}

    def execute_safe_git_update(self, channel: str = "main", dry_run: bool = True) -> Dict[str, Any]:
        run_id = f"update-run-{uuid4().hex[:12]}"
        started_at = self._now()
        git_state = self.current_git_state()
        commands: List[Dict[str, Any]] = []
        status = "dry_run_ready" if dry_run else "blocked"
        if not git_state.get("ok"):
            status = "blocked_git_unavailable"
        elif git_state.get("dirty"):
            status = "blocked_dirty_worktree"
        elif dry_run:
            commands.append({"planned": ["git", "fetch", "origin", channel]})
            commands.append({"planned": ["git", "pull", "--ff-only", "origin", channel]})
        else:
            backup = self.create_backup_manifest()
            commands.append({"backup": backup})
            commands.append(self._run_command(["git", "fetch", "origin", channel], timeout=120))
            if commands[-1].get("ok"):
                commands.append(self._run_command(["git", "pull", "--ff-only", "origin", channel], timeout=120))
            status = "updated" if commands and commands[-1].get("ok") else "failed"
        run = {
            "run_id": run_id,
            "created_at": started_at,
            "channel": channel,
            "dry_run": dry_run,
            "status": status,
            "git_state_before": git_state,
            "commands": commands,
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["runs"].append(run)
            store["runs"] = store["runs"][-100:]
            return store

        UPDATE_STORE.update(mutate)
        return {"ok": True, "mode": "self_update_execute", "run": run}

    def build_dashboard(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "self_update_dashboard",
            "status": self.get_status(),
            "git_state": self.current_git_state(),
            "latest_plan": store.get("plans", [])[-1] if store.get("plans") else None,
            "latest_run": store.get("runs", [])[-1] if store.get("runs") else None,
            "preserve_paths": DEFAULT_PRESERVE_PATHS,
            "managed_paths": DEFAULT_MANAGED_PATHS,
            "answer_to_operator": "Atualizações de código podem ser por git pull no PC local; EXE/APK normalmente precisam de novo build quando muda backend/frontend. A memória fica em data/ e memory/ e deve ser sempre preservada.",
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "self_update_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


self_update_service = SelfUpdateService()
