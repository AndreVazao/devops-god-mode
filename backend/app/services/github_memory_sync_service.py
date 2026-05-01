from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.github_service import github_service
from app.services.memory_core_service import memory_core_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SYNC_FILE = DATA_DIR / "github_memory_sync.json"
SYNC_STORE = AtomicJsonStore(
    SYNC_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "sync_programming_memory_to_andreos_memory_repo_after_repo_work",
        "syncs": [],
    },
)


class GitHubMemorySyncService:
    """Sync technical/programming memory into AndreVazao/andreos-memory.

    This service is intentionally separate from the live local PC memory. The
    GitHub repo stores development context: what changed, why it changed, audit
    notes and next programming steps. It must not become a dump of live runtime
    data, client data or secrets.
    """

    DEFAULT_MEMORY_REPO = "AndreVazao/andreos-memory"
    TARGET_PREFIX = "AndreOS/02_PROJETOS"
    SYNCABLE_FILES = [
        "MEMORIA_MESTRE.md",
        "DECISOES.md",
        "ARQUITETURA.md",
        "BACKLOG.md",
        "ROADMAP.md",
        "HISTORICO.md",
        "ERROS.md",
        "PROMPTS.md",
        "ULTIMA_SESSAO.md",
    ]

    BLOCKED_TEXT = [
        "password",
        "senha",
        "token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "private_key",
        "github_pat",
        "cookie",
        "authorization",
        "bearer",
        "stripe_secret",
        "paypal_secret",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_project(self, project_name: str) -> str:
        return (project_name or "GOD_MODE").strip().upper().replace("-", "_").replace(" ", "_")

    def _contains_blocked_text(self, value: str) -> List[str]:
        lowered = value.lower()
        return [item for item in self.BLOCKED_TEXT if item in lowered]

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "github_memory_sync_policy",
            "memory_repo": self.DEFAULT_MEMORY_REPO,
            "purpose": "programming_context_only",
            "not_for": [
                "live_pc_runtime_memory",
                "client_sensitive_data",
                "tokens_or_passwords",
                "private_runtime_files",
            ],
            "rules": [
                "sync only after repository/programming work",
                "write concise technical context, not full live runtime dumps",
                "block content containing secret-like keywords",
                "write into AndreOS/02_PROJETOS/<PROJECT>/ inside andreos-memory",
                "local PC/Obsidian remains the source for operational work-in-progress",
            ],
            "syncable_files": self.SYNCABLE_FILES,
        }

    async def sync_project(
        self,
        project_name: str,
        commit_message: Optional[str] = None,
        memory_repo: str = DEFAULT_MEMORY_REPO,
        dry_run: bool = False,
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        project = self._normalize_project(project_name)
        selected_files = [item for item in (files or self.SYNCABLE_FILES) if item in self.SYNCABLE_FILES]
        local = memory_core_service.read_project(project)
        memory = local.get("memory") or {}
        planned: List[Dict[str, Any]] = []
        blocked: List[Dict[str, Any]] = []
        written: List[Dict[str, Any]] = []

        for file_name in selected_files:
            content = str(memory.get(file_name) or "").strip()
            if not content:
                continue
            hits = self._contains_blocked_text(content)
            target_path = f"{self.TARGET_PREFIX}/{project}/{file_name}"
            if hits:
                blocked.append({"file": file_name, "path": target_path, "blocked_keywords": hits})
                continue
            planned.append({"file": file_name, "path": target_path, "chars": len(content)})
            if dry_run:
                continue
            existing = await github_service.get_repository_file(memory_repo, target_path, ref="main")
            sha = existing.get("sha") if existing.get("ok") else None
            result = await github_service.create_or_update_repository_file(
                repository_full_name=memory_repo,
                path=target_path,
                content_text=content + "\n",
                commit_message=commit_message or f"memory: sync {project} programming context",
                branch="main",
                sha=sha,
            )
            written.append(result)

        sync = {
            "sync_id": f"github-memory-sync-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "created_at": self._now(),
            "project": project,
            "memory_repo": memory_repo,
            "dry_run": dry_run,
            "planned": planned,
            "blocked": blocked,
            "written": written,
            "status": "blocked" if blocked else ("planned" if dry_run else "synced"),
        }
        self._store(sync)
        return {"ok": len(blocked) == 0, "mode": "github_memory_sync_project", "sync": sync}

    async def record_repo_work_and_sync(
        self,
        project_name: str,
        repo_full_name: str,
        summary: str,
        result: str = "",
        next_steps: str = "",
        memory_repo: str = DEFAULT_MEMORY_REPO,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        combined = "\n".join([project_name, repo_full_name, summary, result, next_steps])
        hits = self._contains_blocked_text(combined)
        if hits:
            return {"ok": False, "mode": "github_memory_sync_record_repo_work", "error": "blocked_secret_keyword", "blocked_keywords": hits}

        project = self._normalize_project(project_name)
        memory_core_service.write_history(
            project,
            action=f"Repo work recorded for {repo_full_name}",
            result=f"Resumo: {summary}\n\nResultado: {result or 'Registado.'}",
        )
        if next_steps:
            memory_core_service.update_last_session(
                project,
                summary=f"Último trabalho técnico registado em {repo_full_name}: {summary}",
                next_steps=next_steps,
            )
        sync = await self.sync_project(
            project_name=project,
            commit_message=f"memory: update {project} after {repo_full_name} work",
            memory_repo=memory_repo,
            dry_run=dry_run,
            files=["HISTORICO.md", "ULTIMA_SESSAO.md", "DECISOES.md", "ARQUITETURA.md", "BACKLOG.md"],
        )
        return {"ok": sync.get("ok", False), "mode": "github_memory_sync_record_repo_work", "project": project, "sync": sync.get("sync")}

    def latest(self) -> Dict[str, Any]:
        state = SYNC_STORE.load()
        syncs = state.get("syncs") or []
        return {
            "ok": True,
            "mode": "github_memory_sync_latest",
            "latest_sync": syncs[-1] if syncs else None,
            "sync_count": len(syncs),
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "github_memory_sync_status",
            "github_configured": github_service.is_configured(),
            "memory_repo": self.DEFAULT_MEMORY_REPO,
            "latest_sync_status": ((latest.get("latest_sync") or {}).get("status")),
            "sync_count": latest.get("sync_count", 0),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "github_memory_sync_panel",
            "headline": "Sync memória técnica/repos para AndreOS Memory GitHub",
            "policy": self.policy(),
            "status": self.get_status(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "policy", "label": "Ver política", "endpoint": "/api/github-memory-sync/policy", "priority": "high"},
                {"id": "sync_project", "label": "Sincronizar projeto", "endpoint": "/api/github-memory-sync/sync-project", "priority": "critical"},
                {"id": "record_repo_work", "label": "Registar trabalho repo", "endpoint": "/api/github-memory-sync/record-repo-work", "priority": "critical"},
            ],
        }

    def _store(self, sync: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "sync_programming_memory_to_andreos_memory_repo_after_repo_work")
            state.setdefault("syncs", [])
            state["syncs"].append(sync)
            state["syncs"] = state["syncs"][-200:]
            return state

        SYNC_STORE.update(mutate)


github_memory_sync_service = GitHubMemorySyncService()
