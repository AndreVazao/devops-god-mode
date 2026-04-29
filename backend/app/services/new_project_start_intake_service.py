from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.operator_priority_service import operator_priority_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
NEW_PROJECT_FILE = DATA_DIR / "new_project_start_intake.json"
NEW_PROJECT_STORE = AtomicJsonStore(
    NEW_PROJECT_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "new_projects_start_from_operator_idea_and_require_approval_before_creation",
        "proposals": [],
        "decisions": [],
    },
)


class NewProjectStartIntakeService:
    """Intake for brand-new projects that do not yet have conversations/repos/files.

    Existing-project recovery is handled by unified intake. This service covers
    the other path: the operator gives a fresh idea and God Mode prepares a
    structured, approval-gated project start proposal.
    """

    PROJECT_TYPES = [
        "app",
        "website",
        "backend",
        "mobile_apk",
        "desktop_exe",
        "automation_bot",
        "content_system",
        "business_system",
        "game_bot",
        "ai_tool",
        "unknown",
    ]

    STACK_PRESETS = {
        "app": ["frontend", "backend", "database", "installer", "docs"],
        "website": ["frontend", "cms/content", "deploy", "seo", "analytics"],
        "backend": ["api", "database", "auth", "workers", "docs"],
        "mobile_apk": ["android", "webview/native shell", "backend link", "pairing", "build artifact"],
        "desktop_exe": ["python", "desktop launcher", "autostart", "packaging", "installer"],
        "automation_bot": ["orchestrator", "scheduler", "approval gates", "logs", "safe runner"],
        "content_system": ["studio", "publisher", "assets", "calendar", "monetization"],
        "business_system": ["crm", "quotes", "jobs", "inventory", "reports"],
        "game_bot": ["runtime", "strategy", "screen/input layer", "safety", "dashboard"],
        "ai_tool": ["prompt router", "memory", "providers", "evaluation", "approval gates"],
        "unknown": ["discovery", "requirements", "architecture", "prototype", "delivery"],
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _slug(self, value: str) -> str:
        safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
        while "--" in safe:
            safe = safe.replace("--", "-")
        return safe.strip("-") or f"new-project-{uuid4().hex[:8]}"

    def _project_id(self, value: str) -> str:
        return self._slug(value).replace("-", "_").upper()

    def template(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "new_project_start_template",
            "fields": [
                {"id": "name", "label": "Nome do projeto", "required": True},
                {"id": "idea", "label": "Ideia em linguagem normal", "required": True},
                {"id": "project_type", "label": "Tipo", "required": False, "options": self.PROJECT_TYPES},
                {"id": "target_platforms", "label": "Plataformas alvo", "required": False, "examples": ["web", "android", "windows", "backend"]},
                {"id": "must_have", "label": "Obrigatório", "required": False},
                {"id": "nice_to_have", "label": "Desejável", "required": False},
                {"id": "deadline", "label": "Urgência/data alvo", "required": False},
            ],
            "quick_examples": [
                "Criar um novo sistema para gerir clientes e orçamentos da ProVentil",
                "Criar um APK simples para controlar o God Mode a partir do telemóvel",
                "Criar um website para publicar histórias dos Baribudos",
                "Criar um bot novo para automatizar uma tarefa repetitiva no PC",
            ],
        }

    def propose(
        self,
        name: str,
        idea: str,
        project_type: str = "unknown",
        target_platforms: Optional[List[str]] = None,
        must_have: Optional[List[str]] = None,
        nice_to_have: Optional[List[str]] = None,
        deadline: Optional[str] = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        clean_type = project_type if project_type in self.PROJECT_TYPES else "unknown"
        project_slug = self._slug(name)
        project_id = self._project_id(name)
        proposal_id = f"new-project-proposal-{uuid4().hex[:12]}"
        platforms = target_platforms or self._infer_platforms(clean_type, idea)
        modules = self.STACK_PRESETS.get(clean_type, self.STACK_PRESETS["unknown"])
        proposal = {
            "proposal_id": proposal_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "proposal_ready_needs_operator_approval",
            "name": name.strip(),
            "project_id": project_id,
            "project_slug": project_slug,
            "repo_name_suggestion": project_slug,
            "project_type": clean_type,
            "idea": idea.strip(),
            "target_platforms": platforms,
            "must_have": must_have or [],
            "nice_to_have": nice_to_have or [],
            "deadline": deadline,
            "suggested_modules": modules,
            "starter_architecture": self._starter_architecture(clean_type, platforms, modules),
            "first_safe_steps": self._first_safe_steps(project_id),
            "approval_gates": self._approval_gates(project_id, project_slug),
            "priority_suggestion": self._priority_suggestion(project_id),
            "destructive_or_external_actions_allowed": False,
            "operator_next": {
                "label": "Aprovar criação do projeto",
                "endpoint": "/api/new-project-start/approve-plan",
                "route": "/app/home",
            },
        }
        self._store_proposal(proposal)
        return {"ok": True, "mode": "new_project_start_proposal", "proposal": proposal}

    def _infer_platforms(self, project_type: str, idea: str) -> List[str]:
        text = idea.lower()
        platforms: List[str] = []
        if any(term in text for term in ["apk", "android", "telemóvel", "mobile"]):
            platforms.append("android")
        if any(term in text for term in ["exe", "windows", "pc", "desktop"]):
            platforms.append("windows")
        if any(term in text for term in ["site", "website", "web", "dashboard"]):
            platforms.append("web")
        if any(term in text for term in ["api", "backend", "servidor"]):
            platforms.append("backend")
        if not platforms:
            if project_type == "mobile_apk":
                platforms = ["android", "backend"]
            elif project_type == "desktop_exe":
                platforms = ["windows", "backend"]
            elif project_type == "website":
                platforms = ["web"]
            elif project_type == "backend":
                platforms = ["backend"]
            else:
                platforms = ["web", "backend"]
        return platforms

    def _starter_architecture(self, project_type: str, platforms: List[str], modules: List[str]) -> Dict[str, Any]:
        return {
            "project_type": project_type,
            "platforms": platforms,
            "modules": modules,
            "recommended_first_repo_layout": [
                "README.md",
                "docs/PROJECT_BRIEF.md",
                "docs/ARCHITECTURE.md",
                "docs/ROADMAP.md",
                "src/",
                "tests/",
                ".github/workflows/",
            ],
            "recommended_delivery_artifacts": self._artifacts_for_platforms(platforms),
            "memory_setup": {
                "create_project_memory": True,
                "template_files": ["MEMORIA_MESTRE.md", "ARQUITETURA.md", "BACKLOG.md", "DECISOES.md", "ROADMAP.md", "ULTIMA_SESSAO.md"],
            },
        }

    def _artifacts_for_platforms(self, platforms: List[str]) -> List[str]:
        artifacts: List[str] = []
        if "android" in platforms:
            artifacts.append("APK debug/release")
        if "windows" in platforms:
            artifacts.append("Windows EXE")
        if "web" in platforms:
            artifacts.append("Web deploy preview")
        if "backend" in platforms:
            artifacts.append("Backend API package")
        return artifacts or ["Project source bundle"]

    def _first_safe_steps(self, project_id: str) -> List[Dict[str, Any]]:
        return [
            {"id": "clarify_requirements", "label": "Clarificar requisitos", "approval_required": False},
            {"id": "draft_project_brief", "label": "Preparar brief do projeto", "approval_required": False},
            {"id": "draft_architecture", "label": "Preparar arquitetura inicial", "approval_required": False},
            {"id": "draft_roadmap", "label": "Preparar roadmap", "approval_required": False},
            {"id": "prepare_repo_plan", "label": "Preparar plano de repo", "approval_required": False},
        ]

    def _approval_gates(self, project_id: str, repo_name: str) -> List[Dict[str, Any]]:
        return [
            {"gate_id": "create_project_memory", "label": f"Criar memória do projeto {project_id}", "requires_operator_ok": True},
            {"gate_id": "create_repo", "label": f"Criar repo {repo_name}", "requires_operator_ok": True},
            {"gate_id": "write_initial_files", "label": "Escrever ficheiros iniciais", "requires_operator_ok": True},
            {"gate_id": "configure_builds", "label": "Configurar builds/workflows", "requires_operator_ok": True},
            {"gate_id": "first_real_build", "label": "Executar primeiro build real", "requires_operator_ok": True},
        ]

    def _priority_suggestion(self, project_id: str) -> Dict[str, Any]:
        priorities = operator_priority_service.get_priorities()
        active_project = ((priorities.get("state") or {}) if priorities.get("ok") else {}).get("active_project") or "GOD_MODE"
        return {
            "suggest_add_to_operator_priorities": True,
            "suggested_project_id": project_id,
            "current_active_project": active_project,
            "default_position": "after_current_active_project",
            "operator_decides_final_order": True,
        }

    def _store_proposal(self, proposal: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "new_projects_start_from_operator_idea_and_require_approval_before_creation")
            state.setdefault("proposals", [])
            state.setdefault("decisions", [])
            state["proposals"].append(proposal)
            state["proposals"] = state["proposals"][-100:]
            return state

        NEW_PROJECT_STORE.update(mutate)

    def approve_plan(self, proposal_id: str, tenant_id: str = "owner-andre", note: str = "operator approved new project start plan") -> Dict[str, Any]:
        state = NEW_PROJECT_STORE.load()
        proposal = next((item for item in state.get("proposals", []) if item.get("proposal_id") == proposal_id), None)
        if not proposal:
            return {"ok": False, "mode": "new_project_start_approve_plan", "error": "proposal_not_found", "proposal_id": proposal_id}
        decision = {
            "decision_id": f"new-project-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "proposal_id": proposal_id,
            "project_id": proposal.get("project_id"),
            "repo_name_suggestion": proposal.get("repo_name_suggestion"),
            "decision": "approved_plan_only",
            "note": note,
            "still_requires_gates_for_repo_and_file_creation": True,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("decisions", [])
            state["decisions"].append(decision)
            state["decisions"] = state["decisions"][-100:]
            for item in state.get("proposals", []):
                if item.get("proposal_id") == proposal_id:
                    item["status"] = "plan_approved_waiting_creation_gates"
                    item["approved_decision_id"] = decision["decision_id"]
            return state

        new_state = NEW_PROJECT_STORE.update(mutate)
        return {
            "ok": True,
            "mode": "new_project_start_plan_approved",
            "decision": decision,
            "proposal": proposal,
            "state": new_state,
            "operator_next": {
                "label": "Criar gates de arranque do projeto",
                "endpoint": "/api/new-project-start/creation-gates",
                "route": "/app/home",
            },
        }

    def creation_gates(self, proposal_id: Optional[str] = None) -> Dict[str, Any]:
        proposal = self._find_proposal(proposal_id)
        if not proposal:
            return {"ok": False, "mode": "new_project_start_creation_gates", "error": "proposal_not_found"}
        return {
            "ok": True,
            "mode": "new_project_start_creation_gates",
            "proposal_id": proposal.get("proposal_id"),
            "project_id": proposal.get("project_id"),
            "repo_name_suggestion": proposal.get("repo_name_suggestion"),
            "gates": proposal.get("approval_gates", []),
            "safe_first_steps": proposal.get("first_safe_steps", []),
            "policy": "repo_memory_files_and_builds_require_operator_confirmation",
        }

    def _find_proposal(self, proposal_id: Optional[str]) -> Optional[Dict[str, Any]]:
        proposals = NEW_PROJECT_STORE.load().get("proposals", [])
        if proposal_id:
            return next((item for item in proposals if item.get("proposal_id") == proposal_id), None)
        return proposals[-1] if proposals else None

    def latest(self) -> Dict[str, Any]:
        state = NEW_PROJECT_STORE.load()
        proposals = state.get("proposals", [])
        decisions = state.get("decisions", [])
        return {
            "ok": True,
            "mode": "new_project_start_latest",
            "latest_proposal": proposals[-1] if proposals else None,
            "latest_decision": decisions[-1] if decisions else None,
            "proposal_count": len(proposals),
            "decision_count": len(decisions),
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        proposal = latest.get("latest_proposal") or {}
        return {
            "ok": True,
            "mode": "new_project_start_status",
            "status": proposal.get("status") or "ready_for_new_project_idea",
            "proposal_count": latest.get("proposal_count", 0),
            "decision_count": latest.get("decision_count", 0),
            "latest_project_id": proposal.get("project_id"),
            "destructive_or_external_actions_allowed": False,
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "new_project_start_panel",
            "headline": "Criar projeto novo do zero",
            "status": self.get_status(),
            "template": self.template(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "template", "label": "Modelo de ideia", "endpoint": "/api/new-project-start/template", "priority": "high"},
                {"id": "latest", "label": "Última proposta", "endpoint": "/api/new-project-start/latest", "priority": "high"},
                {"id": "gates", "label": "Gates criação", "endpoint": "/api/new-project-start/creation-gates", "priority": "high"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "new_project_start_package", "package": {"status": self.get_status(), "panel": self.panel()}}


new_project_start_intake_service = NewProjectStartIntakeService()
