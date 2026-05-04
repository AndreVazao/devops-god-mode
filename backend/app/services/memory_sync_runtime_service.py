from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.github_memory_sync_service import github_memory_sync_service
from app.services.memory_core_service import memory_core_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
RUNTIME_FILE = DATA_DIR / "memory_sync_runtime.json"
RUNTIME_STORE = AtomicJsonStore(
    RUNTIME_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "stable_github_memory_after_merged_phase_with_local_obsidian_note_draft",
        "events": [],
        "packages": [],
        "obsidian_notes": [],
        "sync_runs": [],
    },
)


class MemorySyncRuntimeService:
    """Runtime layer for promoting stable technical memory.

    Phase 169 separates three surfaces:
    - GitHub memory: stable technical decisions, repo work, PRs, phase history.
    - Local/Obsidian notes: workshop notes, drafts and operator-facing continuation notes.
    - Runtime events: structured records that decide what is mature enough to sync.

    It does not store tokens, cookies, passwords, API keys, private runtime dumps,
    customer data or live PC context in GitHub memory.
    """

    SERVICE_ID = "memory_sync_runtime"
    DEFAULT_PROJECT = "GOD_MODE"
    DEFAULT_MEMORY_REPO = "AndreVazao/andreos-memory"
    STABLE_FILES = ["HISTORICO.md", "ULTIMA_SESSAO.md", "DECISOES.md", "ARQUITETURA.md", "BACKLOG.md"]
    OBSIDIAN_NOTE_ROOT = "02_PROJETOS/{project}/99_OFICINA_LOCAL"
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
        "sessionid",
        "refresh_token",
        "access_token",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = RUNTIME_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "github_memory_service_ready": github_memory_sync_service.get_status().get("ok") is True,
            "memory_core_ready": memory_core_service.get_status().get("ok") is True,
            "event_count": len(state.get("events") or []),
            "package_count": len(state.get("packages") or []),
            "sync_run_count": len(state.get("sync_runs") or []),
            "obsidian_note_count": len(state.get("obsidian_notes") or []),
            "stable_files": self.STABLE_FILES,
        }

    def rules(self) -> List[str]:
        return [
            "GitHub memory guarda apenas memória técnica estável de programação/repos.",
            "Obsidian/local guarda oficina, rascunhos, notas de continuação e trabalho vivo local.",
            "Eventos merged_phase podem gerar pacote estável para HISTORICO, ULTIMA_SESSAO e DECISOES.",
            "Conteúdo com keywords de segredo é bloqueado antes de qualquer package/sync.",
            "dry_run=true por defeito em sync runtime.",
            "Notas Obsidian são preparadas como URI/ficheiro sugerido; cloud não depende do Obsidian.",
            "Sync GitHub só chama github_memory_sync_service depois de sanitização e classificação estável.",
        ]

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "purpose": "automatic_stable_memory_sync_after_merged_phase",
            "github_memory": {
                "repo": self.DEFAULT_MEMORY_REPO,
                "scope": "stable_programming_memory",
                "allowed": ["phase summaries", "PR numbers", "merge commits", "technical decisions", "architecture notes", "next programming steps"],
                "blocked": ["live PC runtime", "client data", "tokens", "passwords", "cookies", "API keys", "private dumps"],
            },
            "obsidian_local": {
                "scope": "workshop_and_local_continuation",
                "dependency_policy": "cloud_programs_do_not_depend_on_obsidian",
                "note_root_template": self.OBSIDIAN_NOTE_ROOT,
            },
            "blocked_text": self.BLOCKED_TEXT,
            "stable_files": self.STABLE_FILES,
            "rules": self.rules(),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            **self.status(),
            "headline": "Memory Sync Runtime",
            "description": "Promove eventos técnicos maduros para AndreOS GitHub memory e prepara notas Obsidian locais sem misturar rascunho com decisão estável.",
            "primary_actions": [
                {"label": "Registar fase merged", "endpoint": "/api/memory-sync-runtime/register-merged-phase", "method": "POST", "safe": True},
                {"label": "Construir pacote", "endpoint": "/api/memory-sync-runtime/build-package", "method": "POST", "safe": True},
                {"label": "Preparar nota Obsidian", "endpoint": "/api/memory-sync-runtime/prepare-obsidian-note", "method": "POST", "safe": True},
                {"label": "Sync estável", "endpoint": "/api/memory-sync-runtime/sync-stable", "method": "POST", "safe": False},
            ],
            "policy": self.policy(),
            "latest": self.latest(),
        }

    def register_merged_phase(
        self,
        phase_number: int,
        phase_title: str,
        repo_full_name: str,
        pr_number: int,
        merge_commit: str,
        summary: str,
        validation: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None,
        next_phase: Optional[str] = None,
        project_name: str = DEFAULT_PROJECT,
    ) -> Dict[str, Any]:
        payload_text = "\n".join(
            [
                str(phase_number),
                phase_title,
                repo_full_name,
                str(pr_number),
                merge_commit,
                summary,
                "\n".join(validation or []),
                "\n".join(decisions or []),
                next_phase or "",
                project_name,
            ]
        )
        safety = self._validate_safe_text(payload_text)
        if not safety.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "blocked_secret_keyword", "blocked_keywords": safety.get("blocked_keywords")}

        event = {
            "event_id": f"memory-event-{uuid4().hex[:12]}",
            "event_type": "merged_phase",
            "created_at": self._now(),
            "project": self._normalize_project(project_name),
            "phase_number": phase_number,
            "phase_title": phase_title.strip(),
            "repo_full_name": repo_full_name.strip(),
            "pr_number": pr_number,
            "merge_commit": merge_commit.strip(),
            "summary": summary.strip(),
            "validation": validation or [],
            "decisions": decisions or [],
            "next_phase": next_phase or "",
            "stable_candidate": True,
            "status": "registered",
        }
        self._store("events", event)
        return {"ok": True, "service": self.SERVICE_ID, "event": event}

    def build_package(self, event_id: str, include_obsidian_note: bool = True) -> Dict[str, Any]:
        event = self._find("events", event_id, "event_id")
        if not event:
            return {"ok": False, "service": self.SERVICE_ID, "error": "event_not_found", "event_id": event_id}
        if event.get("event_type") != "merged_phase":
            return {"ok": False, "service": self.SERVICE_ID, "error": "unsupported_event_type", "event_type": event.get("event_type")}

        stable = self._stable_memory_entries(event)
        safety = self._validate_safe_text("\n".join(stable.values()))
        if not safety.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "blocked_secret_keyword", "blocked_keywords": safety.get("blocked_keywords")}

        package = {
            "package_id": f"memory-package-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "event_id": event_id,
            "project": event.get("project"),
            "classification": "stable_programming_memory",
            "target_memory_repo": self.DEFAULT_MEMORY_REPO,
            "stable_entries": stable,
            "files_to_sync": self.STABLE_FILES,
            "include_obsidian_note": include_obsidian_note,
            "obsidian_note": self._obsidian_note(event) if include_obsidian_note else None,
            "status": "package_ready",
        }
        self._store("packages", package)
        if include_obsidian_note and package.get("obsidian_note"):
            self._store("obsidian_notes", package["obsidian_note"])
        return {"ok": True, "service": self.SERVICE_ID, "package": package}

    def prepare_obsidian_note(self, event_id: str) -> Dict[str, Any]:
        event = self._find("events", event_id, "event_id")
        if not event:
            return {"ok": False, "service": self.SERVICE_ID, "error": "event_not_found", "event_id": event_id}
        note = self._obsidian_note(event)
        safety = self._validate_safe_text(note.get("content", ""))
        if not safety.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "blocked_secret_keyword", "blocked_keywords": safety.get("blocked_keywords")}
        self._store("obsidian_notes", note)
        return {"ok": True, "service": self.SERVICE_ID, "note": note}

    async def sync_stable_package(
        self,
        package_id: str,
        dry_run: bool = True,
        memory_repo: str = DEFAULT_MEMORY_REPO,
    ) -> Dict[str, Any]:
        package = self._find("packages", package_id, "package_id")
        if not package:
            return {"ok": False, "service": self.SERVICE_ID, "error": "package_not_found", "package_id": package_id}

        safety = self._validate_safe_text(str(package.get("stable_entries") or {}))
        if not safety.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "blocked_secret_keyword", "blocked_keywords": safety.get("blocked_keywords")}

        project = self._normalize_project(str(package.get("project") or self.DEFAULT_PROJECT))
        entries = package.get("stable_entries") or {}

        if not dry_run:
            for file_name, entry in entries.items():
                if file_name == "HISTORICO.md":
                    memory_core_service.write_history(project, action=entry.get("title", "Memory sync runtime"), result=entry.get("body", ""))
                elif file_name == "DECISOES.md":
                    for decision in entry.get("decisions", []):
                        memory_core_service.write_decision(project, decision=decision, reason=entry.get("reason", "Phase merged and validated."))
                elif file_name == "ULTIMA_SESSAO.md":
                    memory_core_service.update_last_session(project, summary=entry.get("summary", ""), next_steps=entry.get("next_steps", ""))
                elif file_name == "BACKLOG.md" and entry.get("next_task"):
                    memory_core_service.add_backlog_task(project, task=entry["next_task"], priority="high")

        sync_result = await github_memory_sync_service.sync_project(
            project_name=project,
            commit_message=f"memory: sync {project} after merged phase",
            memory_repo=memory_repo,
            dry_run=dry_run,
            files=package.get("files_to_sync") or self.STABLE_FILES,
        )
        run = {
            "sync_run_id": f"memory-sync-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "package_id": package_id,
            "project": project,
            "dry_run": dry_run,
            "memory_repo": memory_repo,
            "status": "dry_run_completed" if dry_run else ("synced" if sync_result.get("ok") else "sync_failed"),
            "github_memory_sync": sync_result,
        }
        self._store("sync_runs", run)
        return {"ok": sync_result.get("ok", False) if not dry_run else True, "service": self.SERVICE_ID, "run": run}

    def end_to_end_preview(
        self,
        phase_number: int,
        phase_title: str,
        repo_full_name: str,
        pr_number: int,
        merge_commit: str,
        summary: str,
        validation: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None,
        next_phase: Optional[str] = None,
        project_name: str = DEFAULT_PROJECT,
    ) -> Dict[str, Any]:
        event = self.register_merged_phase(
            phase_number=phase_number,
            phase_title=phase_title,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            merge_commit=merge_commit,
            summary=summary,
            validation=validation,
            decisions=decisions,
            next_phase=next_phase,
            project_name=project_name,
        )
        if not event.get("ok"):
            return event
        package = self.build_package(event_id=event["event"]["event_id"], include_obsidian_note=True)
        return {"ok": package.get("ok", False), "service": self.SERVICE_ID, "event": event.get("event"), "package": package.get("package")}

    def latest(self) -> Dict[str, Any]:
        state = RUNTIME_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "latest_event": (state.get("events") or [None])[-1],
            "latest_package": (state.get("packages") or [None])[-1],
            "latest_obsidian_note": (state.get("obsidian_notes") or [None])[-1],
            "latest_sync_run": (state.get("sync_runs") or [None])[-1],
            "event_count": len(state.get("events") or []),
            "package_count": len(state.get("packages") or []),
            "sync_run_count": len(state.get("sync_runs") or []),
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "policy": self.policy(), "latest": self.latest()}

    def _stable_memory_entries(self, event: Dict[str, Any]) -> Dict[str, Any]:
        phase_label = f"Phase {event.get('phase_number')} — {event.get('phase_title')}"
        validation_lines = "\n".join(f"- {item}" for item in event.get("validation") or []) or "- Validação não especificada."
        next_phase = event.get("next_phase") or "Próxima fase não definida."
        return {
            "HISTORICO.md": {
                "title": phase_label,
                "body": (
                    f"Repo: `{event.get('repo_full_name')}`\n\n"
                    f"PR: #{event.get('pr_number')}\n\n"
                    f"Merge commit: `{event.get('merge_commit')}`\n\n"
                    f"Resumo: {event.get('summary')}\n\n"
                    f"Validação:\n{validation_lines}"
                ),
            },
            "ULTIMA_SESSAO.md": {
                "summary": f"{phase_label} merged em `{event.get('repo_full_name')}` via PR #{event.get('pr_number')}. {event.get('summary')}",
                "next_steps": next_phase,
            },
            "DECISOES.md": {
                "decisions": event.get("decisions") or [],
                "reason": f"{phase_label} foi merged e validada.",
            },
            "BACKLOG.md": {
                "next_task": next_phase,
            },
            "ARQUITETURA.md": {
                "note": f"{phase_label}: alteração técnica estável ligada ao runtime de memória/sync.",
            },
        }

    def _obsidian_note(self, event: Dict[str, Any]) -> Dict[str, Any]:
        project = self._normalize_project(str(event.get("project") or self.DEFAULT_PROJECT))
        safe_title = self._slug(f"phase-{event.get('phase_number')}-{event.get('phase_title')}")
        note_path = f"{self.OBSIDIAN_NOTE_ROOT.format(project=project)}/{safe_title}.md"
        validation_lines = "\n".join(f"- {item}" for item in event.get("validation") or []) or "- Validação não especificada."
        decisions = "\n".join(f"- {item}" for item in event.get("decisions") or []) or "- Sem decisão nova registada."
        content = (
            f"# Oficina local — Phase {event.get('phase_number')} — {event.get('phase_title')}\n\n"
            f"## Estado\nMerged e validada.\n\n"
            f"## Repo\n`{event.get('repo_full_name')}`\n\n"
            f"## PR\n#{event.get('pr_number')}\n\n"
            f"## Merge commit\n`{event.get('merge_commit')}`\n\n"
            f"## Resumo\n{event.get('summary')}\n\n"
            f"## Validação\n{validation_lines}\n\n"
            f"## Decisões\n{decisions}\n\n"
            f"## Próxima fase\n{event.get('next_phase') or 'Não definida.'}\n\n"
            "> Nota local/oficina. Programas cloud não dependem desta nota Obsidian.\n"
        )
        return {
            "note_id": f"obsidian-note-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project": project,
            "note_path": note_path,
            "content": content,
            "classification": "local_workshop_note",
            "promote_to_github_memory": False,
        }

    def _validate_safe_text(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        hits = [keyword for keyword in self.BLOCKED_TEXT if re.search(rf"(?<![a-z0-9_]){re.escape(keyword)}(?![a-z0-9_])", lowered)]
        return {"ok": not hits, "blocked_keywords": hits}

    def _normalize_project(self, project_name: str) -> str:
        return re.sub(r"[^A-Z0-9_]+", "_", (project_name or self.DEFAULT_PROJECT).upper()).strip("_") or self.DEFAULT_PROJECT

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug[:90] or "memory-sync-note"

    def _find(self, key: str, value: str, id_key: str) -> Optional[Dict[str, Any]]:
        items = RUNTIME_STORE.load().get(key, [])
        return next((item for item in items if item.get(id_key) == value), None)

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "stable_github_memory_after_merged_phase_with_local_obsidian_note_draft")
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-200:]
            return state

        RUNTIME_STORE.update(mutate)


memory_sync_runtime_service = MemorySyncRuntimeService()
