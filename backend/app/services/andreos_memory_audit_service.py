from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.memory_core_service import PROJECTS_ROOT, PROJECT_FILES, VAULT_ROOT, memory_core_service


class AndreOSMemoryAuditService:
    """Deep audit and safe rehearsal for AndreOS/Obsidian memory."""

    EXPECTED_PROJECTS = [
        "GOD_MODE",
        "PROVENTIL",
        "VERBAFORGE",
        "BOT_LORDS_MOBILE",
        "ECU_REPRO",
        "BUILD_CONTROL_CENTER",
        "BARIBUDOS_STUDIO",
        "BARIBUDOS_STUDIO_WEBSITE",
        "BOT_FACTORY",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_audit(self, run_rehearsal: bool = True) -> Dict[str, Any]:
        init = memory_core_service.initialize()
        projects = [self._audit_project(project) for project in self.EXPECTED_PROJECTS]
        missing_projects = [project for project in projects if not project["folder_exists"] or project["missing_files"]]
        secret_probe = self._secret_guard_probe()
        context_probe = self._context_probe()
        obsidian_probe = self._obsidian_probe()
        rehearsal = self._rehearsal() if run_rehearsal else {"ok": True, "skipped": True, "summary": "skipped"}
        checks = [
            self._check("structure", "Estrutura AndreOS existe", bool(init.get("ok")), str(VAULT_ROOT)),
            self._check("projects", "Projetos principais existem", not missing_projects, f"{len(projects)} projetos auditados"),
            self._check("secret_guard", "Filtro de segredos bloqueia termos sensíveis", secret_probe.get("blocked") is True, secret_probe.get("detail")),
            self._check("compact_context", "Contexto compacto funciona", context_probe.get("ok") is True and context_probe.get("chars", 0) > 0, f"{context_probe.get('chars', 0)} chars"),
            self._check("obsidian_links", "Links Obsidian são gerados", obsidian_probe.get("ok") is True, obsidian_probe.get("open_uri")),
            self._check("rehearsal", "Ensaio real não destrutivo passou", rehearsal.get("ok") is True, rehearsal.get("summary")),
        ]
        failed = [check for check in checks if not check["ok"]]
        score = round((sum(1 for check in checks if check["ok"]) / len(checks)) * 100) if checks else 0
        return {
            "ok": True,
            "mode": "andreos_memory_audit",
            "created_at": self._now(),
            "status": "ready" if not failed else ("attention" if score >= 70 else "blocked"),
            "score": score,
            "checks": checks,
            "failed_checks": failed,
            "projects": projects,
            "missing_projects": missing_projects,
            "secret_probe": secret_probe,
            "context_probe": context_probe,
            "obsidian_probe": obsidian_probe,
            "rehearsal": rehearsal,
            "operator_next": self._next_action(failed),
        }

    def _audit_project(self, project: str) -> Dict[str, Any]:
        created = memory_core_service.create_project(project)
        normalized = created.get("project", project)
        folder = PROJECTS_ROOT / normalized
        existing_files = [file_name for file_name in PROJECT_FILES if (folder / file_name).exists()]
        missing_files = [file_name for file_name in PROJECT_FILES if file_name not in existing_files]
        file_sizes = {file_name: (folder / file_name).stat().st_size for file_name in existing_files}
        return {
            "project": normalized,
            "folder": str(folder),
            "folder_exists": folder.exists(),
            "file_count": len(existing_files),
            "expected_file_count": len(PROJECT_FILES),
            "missing_files": missing_files,
            "file_sizes": file_sizes,
            "obsidian_master": memory_core_service.obsidian_link(normalized, "MEMORIA_MESTRE.md").get("open_uri"),
        }

    def _secret_guard_probe(self) -> Dict[str, Any]:
        unsafe = memory_core_service.write_history(
            "GOD_MODE",
            "AndreOS audit unsafe probe",
            "Este teste deve bloquear password, token e bearer sem gravar segredos reais.",
        )
        safe = memory_core_service.write_history(
            "GOD_MODE",
            "AndreOS audit safe probe",
            "Teste seguro: confirmar que histórico aceita texto operacional sem credenciais.",
        )
        return {
            "ok": safe.get("ok") is True and unsafe.get("ok") is False,
            "blocked": unsafe.get("ok") is False,
            "safe_write_ok": safe.get("ok") is True,
            "blocked_keywords": unsafe.get("blocked_keywords", []),
            "detail": unsafe.get("error") or unsafe.get("message"),
        }

    def _context_probe(self) -> Dict[str, Any]:
        context = memory_core_service.compact_context("GOD_MODE", max_chars=2400)
        text = context.get("context", "")
        return {
            "ok": context.get("ok") is True,
            "project": context.get("project"),
            "chars": context.get("chars", 0),
            "has_last_session": "ULTIMA_SESSAO" in text,
            "has_decisions": "DECISOES" in text,
        }

    def _obsidian_probe(self) -> Dict[str, Any]:
        link = memory_core_service.obsidian_link("GOD_MODE", "MEMORIA_MESTRE.md")
        return {
            "ok": link.get("ok") is True and str(link.get("open_uri", "")).startswith("obsidian://open?"),
            "open_uri": link.get("open_uri"),
            "new_uri": link.get("new_uri"),
        }

    def _rehearsal(self) -> Dict[str, Any]:
        project = "GOD_MODE"
        decision = memory_core_service.write_decision(
            project,
            "AndreOS Memory Audit rehearsal validated continuity flow.",
            "Phase 90 proves decisions, history, backlog and last session keep project direction.",
        )
        history = memory_core_service.write_history(
            project,
            "AndreOS Memory Audit rehearsal",
            "Validated non-destructive memory flow for daily operator usage.",
        )
        backlog = memory_core_service.add_backlog_task(
            project,
            "Keep Home, Modo fácil, Daily Command Router and AndreOS memory aligned after each phase.",
            priority="high",
        )
        last_session = memory_core_service.update_last_session(
            project,
            "Phase 90 rehearsed AndreOS Memory Core with safe writes and compact context.",
            "Continue improving God Mode as a mobile-first operator system that does not lose project context.",
        )
        context = memory_core_service.compact_context(project, max_chars=3200)
        writes = {"decision": decision, "history": history, "backlog": backlog, "last_session": last_session}
        ok = all(item.get("ok") is True for item in writes.values()) and context.get("ok") is True and context.get("chars", 0) > 0
        return {
            "ok": ok,
            "summary": "safe memory rehearsal completed" if ok else "memory rehearsal failed",
            "writes": writes,
            "context_chars": context.get("chars", 0),
            "context_preview": (context.get("context") or "")[-800:],
        }

    def _check(self, check_id: str, label: str, ok: bool, detail: Any = "") -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok), "detail": detail}

    def _next_action(self, failed: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not failed:
            return {"label": "Continuar a usar Modo fácil com memória AndreOS ativa", "route": "/app/home"}
        first = failed[0]
        return {"label": f"Corrigir memória: {first['label']}", "endpoint": "/api/andreos-memory-audit/audit"}

    def get_status(self) -> Dict[str, Any]:
        audit = self.build_audit(run_rehearsal=False)
        return {
            "ok": True,
            "mode": "andreos_memory_audit_status",
            "status": audit["status"],
            "score": audit["score"],
            "failed_count": len(audit["failed_checks"]),
            "project_count": len(audit["projects"]),
            "operator_next": audit["operator_next"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "andreos_memory_audit_package", "package": {"status": self.get_status(), "audit": self.build_audit(run_rehearsal=True)}}


andreos_memory_audit_service = AndreOSMemoryAuditService()
