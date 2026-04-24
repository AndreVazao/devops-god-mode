from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.project_bootstrap_cockpit_service import project_bootstrap_cockpit_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
COMMAND_MEMORY_FILE = DATA_DIR / "operator_command_intake_memory.json"
COMMAND_MEMORY_STORE = AtomicJsonStore(COMMAND_MEMORY_FILE, default_factory=lambda: {"projects": {}, "commands": []})

PROJECT_MEMORY_ALIASES = {
    "devops-god-mode": "GOD_MODE",
    "godmode": "GOD_MODE",
    "god-mode": "GOD_MODE",
    "general-intake": "GOD_MODE",
    "proventil": "PROVENTIL",
    "verbaforge": "VERBAFORGE",
    "botfarm-headless": "BOT_LORDS_MOBILE",
    "bot-lords-mobile": "BOT_LORDS_MOBILE",
    "ecu-repro": "ECU_REPRO",
    "build-control-center": "BUILD_CONTROL_CENTER",
}


class OperatorCommandIntakeService:
    """Natural command intake layer for God Mode mobile/PC operation."""

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_command_intake_status",
            "status": "operator_command_intake_ready",
            "memory_file": str(COMMAND_MEMORY_FILE),
            "atomic_store_enabled": True,
            "memory_core_enabled": True,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(memory, dict):
            return {"projects": {}, "commands": []}
        memory.setdefault("projects", {})
        memory.setdefault("commands", [])
        return memory

    def _load_memory(self) -> Dict[str, Any]:
        return self._normalize_memory(COMMAND_MEMORY_STORE.load())

    def _save_memory(self, memory: Dict[str, Any]) -> None:
        COMMAND_MEMORY_STORE.save(self._normalize_memory(memory))

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized or "godmode-project"

    def _memory_project_name(self, project: Dict[str, Any]) -> str:
        project_id = project.get("project_id", "general-intake")
        project_name = project.get("project_name", project_id)
        return PROJECT_MEMORY_ALIASES.get(project_id, PROJECT_MEMORY_ALIASES.get(self._slugify(project_name), project_id.replace("-", "_").upper()))

    def _memory_snapshot(self, project: Dict[str, Any]) -> Dict[str, Any]:
        memory_project = self._memory_project_name(project)
        memory_core_service.initialize()
        memory_core_service.create_project(memory_project)
        context = memory_core_service.compact_context(memory_project, max_chars=6000)
        return {
            "memory_project": memory_project,
            "context_available": context.get("ok") is True and context.get("chars", 0) > 0,
            "context_chars": context.get("chars", 0),
            "context_preview": context.get("context", "")[:1200],
            "obsidian": memory_core_service.obsidian_link(memory_project, "MEMORIA_MESTRE.md"),
        }

    def _safe_memory_history(self, project: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
        memory_project = self._memory_project_name(project)
        return memory_core_service.write_history(
            memory_project,
            action="Comando recebido no Operator Command Intake",
            result=f"Intent: {command.get('intent')} | Priority: {command.get('priority')} | Command ID: {command.get('command_id')}",
        )

    def _has_any_term(self, lowered_text: str, terms: List[str]) -> bool:
        for term in terms:
            normalized = term.lower().strip()
            if not normalized:
                continue
            pattern = r"(?<![a-z0-9])" + re.escape(normalized) + r"(?![a-z0-9])"
            if re.search(pattern, lowered_text):
                return True
        return False

    def _guess_project(self, command_text: str, project_hint: str | None = None) -> Dict[str, Any]:
        if project_hint and project_hint.strip():
            name = project_hint.strip()
        else:
            lowered = command_text.lower()
            if "baribudos" in lowered or "bodybou" in lowered or "very good" in lowered:
                name = "baribudos-studio"
            elif "proventil" in lowered:
                name = "proventil"
            elif "verbaforge" in lowered or "verba forge" in lowered:
                name = "verbaforge"
            elif "ecu" in lowered or "repro" in lowered:
                name = "ecu-repro"
            elif "build control" in lowered or "build center" in lowered:
                name = "build-control-center"
            elif "god mode" in lowered or "godmode" in lowered:
                name = "devops-god-mode"
            elif "website" in lowered and "studio" in lowered:
                name = "studio-website-suite"
            elif "botfarm" in lowered or "bot farm" in lowered or "headless" in lowered or "lords mobile" in lowered:
                name = "botfarm-headless"
            else:
                name = "general-intake"
        return {"project_name": name, "project_id": self._slugify(name)}

    def _classify_intent(self, command_text: str) -> Dict[str, Any]:
        lowered = command_text.lower()
        intent = "general_command"
        priority = "medium"
        destructive = False
        approval_required = True

        if self._has_any_term(lowered, ["audita", "auditoria", "verifica", "check", "erros", "partido"]):
            intent = "deep_project_audit"
            priority = "high"
        if self._has_any_term(lowered, ["corrige", "corrigir", "repara", "arruma", "aplica"]):
            intent = "repair_plan"
            priority = "high"
        if self._has_any_term(lowered, ["deploy", "vercel", "render", "supabase", "build", "artifact", "artefact"]):
            intent = "deploy_or_build_readiness"
            priority = "high"
        if self._has_any_term(lowered, ["conversa", "chatgpt", "claude", "gemini", "grok", "deepseek"]):
            intent = "multi_ai_conversation_mapping"
            priority = "high"
        if self._has_any_term(lowered, ["apaga", "delete", "remove repo", "apagar repo", "apagar branch"]):
            destructive = True
            priority = "critical"

        return {
            "intent": intent,
            "priority": priority,
            "destructive": destructive,
            "approval_required": approval_required,
        }

    def _extract_targets(self, command_text: str) -> Dict[str, Any]:
        lowered = command_text.lower()
        providers: List[str] = []
        for provider in ["chatgpt", "claude", "gemini", "grok", "deepseek", "github", "vercel", "render", "supabase"]:
            if self._has_any_term(lowered, [provider]):
                providers.append(provider)
        repos: List[str] = []
        if self._has_any_term(lowered, ["studio"]):
            repos.append("studio")
        if self._has_any_term(lowered, ["website", "site"]):
            repos.append("website")
        if self._has_any_term(lowered, ["backend", "back end"]):
            repos.append("backend")
        if self._has_any_term(lowered, ["frontend", "front end"]):
            repos.append("frontend")
        return {
            "providers": providers,
            "repo_roles": repos,
            "needs_vault": self._has_any_term(lowered, ["token", "secret", "key", "chave", "supabase", "vercel", "render"]),
            "needs_mobile_approval": True,
            "needs_pc_execution": True,
        }

    def _build_execution_plan(self, command: Dict[str, Any], project: Dict[str, Any], targets: Dict[str, Any]) -> List[Dict[str, Any]]:
        intent = command["intent"]
        steps: List[Dict[str, Any]] = [
            {"step_id": "load-andreos-project-memory", "label": "Ler memória AndreOS do projeto antes de planear", "executor": "memory_core", "approval_required": False, "status": "planned"},
            {"step_id": "attach-command-to-project-memory", "label": "Associar pedido ao projeto certo", "executor": "pc_local_brain", "approval_required": False, "status": "planned"},
            {"step_id": "load-project-bootstrap-readiness", "label": "Ler readiness do Project Bootstrap Cockpit", "executor": "pc_local_brain", "approval_required": False, "status": "planned"},
        ]
        if intent in {"deep_project_audit", "repair_plan"}:
            steps.extend([
                {"step_id": "map-related-repositories", "label": "Mapear repos relacionados e papéis frontend/backend/site/cockpit", "executor": "github_provider", "approval_required": False, "status": "planned"},
                {"step_id": "scan-repo-files-and-dependencies", "label": "Auditar ficheiros, imports, rotas, workflows e env vars esperadas", "executor": "pc_local_brain", "approval_required": False, "status": "planned"},
                {"step_id": "prepare-approval-gated-fix-plan", "label": "Preparar plano de correção com PR limpa e pontos de aprovação", "executor": "pc_local_brain", "approval_required": True, "status": "planned"},
            ])
        if intent == "multi_ai_conversation_mapping":
            steps.extend([
                {"step_id": "inventory-ai-conversations", "label": "Inventariar conversas multi-IA ligadas ao projeto", "executor": "browser_provider_bridge", "approval_required": True, "status": "planned"},
                {"step_id": "summarize-and-link-conversations", "label": "Resumir conversas e ligar a projeto/repos", "executor": "pc_local_brain", "approval_required": False, "status": "planned"},
            ])
        if intent == "deploy_or_build_readiness" or targets.get("needs_vault"):
            steps.extend([
                {"step_id": "resolve-vault-secrets-for-project", "label": "Resolver secrets/tokens do projeto no vault sem escrever no Obsidian", "executor": "secret_vault", "approval_required": True, "status": "planned"},
                {"step_id": "validate-build-and-deploy-targets", "label": "Validar GitHub Actions, artifacts, Vercel, Render e Supabase", "executor": "provider_bridge", "approval_required": False, "status": "planned"},
            ])
        if command.get("destructive"):
            steps.append({"step_id": "hard-stop-destructive-action", "label": "Bloquear ação destrutiva até aprovação explícita no cockpit mobile", "executor": "mobile_approval_cockpit", "approval_required": True, "status": "blocked_until_operator_approval"})
        steps.extend([
            {"step_id": "persist-session-memory", "label": "Atualizar histórico e última sessão no AndreOS Memory Core", "executor": "memory_core", "approval_required": False, "status": "planned"},
            {"step_id": "report-back-to-mobile-cockpit", "label": "Enviar progresso, próximos passos e pedidos de aprovação ao telemóvel", "executor": "mobile_cockpit", "approval_required": False, "status": "planned"},
        ])
        return steps

    def submit_command(self, command_text: str, tenant_id: str = "owner-andre", project_hint: str | None = None, source_channel: str = "mobile_chat") -> Dict[str, Any]:
        text = command_text.strip()
        if not text:
            return {"ok": False, "error": "command_text_empty"}
        project = self._guess_project(text, project_hint=project_hint)
        memory_snapshot = self._memory_snapshot(project)
        command_class = self._classify_intent(text)
        targets = self._extract_targets(text)
        command_id = f"cmd-{uuid4().hex[:12]}"
        created_at = self._now()
        bootstrap = project_bootstrap_cockpit_service.build_dashboard(tenant_id=tenant_id, project_name=project["project_name"], providers=["github", "vercel", "supabase", "render"], multirepo_mode=True)
        command = {
            "command_id": command_id,
            "tenant_id": tenant_id,
            "source_channel": source_channel,
            "created_at": created_at,
            "raw_text": text,
            **command_class,
            "project": project,
            "memory_core": memory_snapshot,
            "targets": targets,
            "bootstrap_summary": {"launch_ready": bootstrap.get("launch_ready"), "readiness_score": bootstrap.get("readiness_score"), "blocker_count": bootstrap.get("blocker_count")},
        }
        command["execution_plan"] = self._build_execution_plan(command, project, targets)

        def mutate(memory: Dict[str, Any]) -> Dict[str, Any]:
            memory = self._normalize_memory(memory)
            project_record = memory["projects"].setdefault(project["project_id"], {"project_id": project["project_id"], "project_name": project["project_name"], "created_at": created_at, "last_seen_at": created_at, "command_ids": [], "known_repo_roles": [], "known_providers": [], "memory_project": memory_snapshot["memory_project"]})
            project_record["project_name"] = project["project_name"]
            project_record["memory_project"] = memory_snapshot["memory_project"]
            project_record["last_seen_at"] = created_at
            project_record["command_ids"].append(command_id)
            project_record["known_repo_roles"] = sorted(set(project_record.get("known_repo_roles", [])) | set(targets.get("repo_roles", [])))
            project_record["known_providers"] = sorted(set(project_record.get("known_providers", [])) | set(targets.get("providers", [])))
            memory["commands"].append(command)
            memory["commands"] = memory["commands"][-500:]
            return memory

        update_result = COMMAND_MEMORY_STORE.update(mutate)
        memory = self._normalize_memory(update_result["payload"])
        memory_history = self._safe_memory_history(project, command)
        return {"ok": True, "mode": "operator_command_intake_submit", "command": command, "project_memory": memory["projects"][project["project_id"]], "memory_history": memory_history}

    def list_commands(self, tenant_id: str = "owner-andre", project_id: str | None = None, limit: int = 50) -> Dict[str, Any]:
        memory = self._load_memory()
        commands = [item for item in memory.get("commands", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            commands = [item for item in commands if item.get("project", {}).get("project_id") == project_id]
        commands = commands[-max(min(limit, 200), 1):]
        return {"ok": True, "mode": "operator_command_intake_list", "tenant_id": tenant_id, "project_id": project_id, "command_count": len(commands), "commands": commands}

    def list_project_memory(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        memory = self._load_memory()
        projects = list(memory.get("projects", {}).values())
        return {"ok": True, "mode": "operator_command_intake_project_memory", "tenant_id": tenant_id, "project_count": len(projects), "projects": sorted(projects, key=lambda item: item.get("last_seen_at", ""), reverse=True)}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "operator_command_intake_package", "package": {"status": self.get_status(), "project_memory": self.list_project_memory()}}


operator_command_intake_service = OperatorCommandIntakeService()
