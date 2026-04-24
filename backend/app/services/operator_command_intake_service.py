from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.project_bootstrap_cockpit_service import project_bootstrap_cockpit_service

DATA_DIR = Path("data")
COMMAND_MEMORY_FILE = DATA_DIR / "operator_command_intake_memory.json"


class OperatorCommandIntakeService:
    """Natural command intake layer for God Mode mobile/PC operation.

    This service turns a raw operator message into a structured operational command,
    attaches it to a project memory record and creates the first execution plan that
    later phases can expand into repo audits, provider logins, vault-aware deploys
    and approval-gated code changes.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_command_intake_status",
            "status": "operator_command_intake_ready",
            "memory_file": str(COMMAND_MEMORY_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_memory(self) -> Dict[str, Any]:
        if not COMMAND_MEMORY_FILE.exists():
            return {"projects": {}, "commands": []}
        try:
            loaded = json.loads(COMMAND_MEMORY_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"projects": {}, "commands": []}
            loaded.setdefault("projects", {})
            loaded.setdefault("commands", [])
            return loaded
        except json.JSONDecodeError:
            return {"projects": {}, "commands": []}

    def _save_memory(self, memory: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        COMMAND_MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized or "godmode-project"

    def _guess_project(self, command_text: str, project_hint: str | None = None) -> Dict[str, Any]:
        if project_hint and project_hint.strip():
            name = project_hint.strip()
        else:
            lowered = command_text.lower()
            if "baribudos" in lowered or "bodybou" in lowered or "very good" in lowered:
                name = "baribudos-studio"
            elif "god mode" in lowered or "godmode" in lowered:
                name = "devops-god-mode"
            elif "website" in lowered and "studio" in lowered:
                name = "studio-website-suite"
            elif "botfarm" in lowered or "bot farm" in lowered or "headless" in lowered:
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

        if any(word in lowered for word in ["audita", "auditoria", "verifica", "check", "erros", "partido"]):
            intent = "deep_project_audit"
            priority = "high"
        if any(word in lowered for word in ["corrige", "corrigir", "repara", "arruma", "aplica"]):
            intent = "repair_plan"
            priority = "high"
        if any(word in lowered for word in ["deploy", "vercel", "render", "supabase", "build", "artifact", "artefact"]):
            intent = "deploy_or_build_readiness"
            priority = "high"
        if any(word in lowered for word in ["conversa", "chatgpt", "claude", "gemini", "grok", "deepseek"]):
            intent = "multi_ai_conversation_mapping"
            priority = "high"
        if any(word in lowered for word in ["apaga", "delete", "remove repo", "apagar repo", "apagar branch"]):
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
            if provider in lowered:
                providers.append(provider)
        repos: List[str] = []
        if "studio" in lowered:
            repos.append("studio")
        if "website" in lowered or "site" in lowered:
            repos.append("website")
        if "backend" in lowered or "back end" in lowered:
            repos.append("backend")
        if "frontend" in lowered or "front end" in lowered:
            repos.append("frontend")
        return {
            "providers": providers,
            "repo_roles": repos,
            "needs_vault": any(item in lowered for item in ["token", "secret", "key", "chave", "supabase", "vercel", "render"]),
            "needs_mobile_approval": True,
            "needs_pc_execution": True,
        }

    def _build_execution_plan(
        self,
        command: Dict[str, Any],
        project: Dict[str, Any],
        targets: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        intent = command["intent"]
        steps: List[Dict[str, Any]] = [
            {
                "step_id": "attach-command-to-project-memory",
                "label": "Associar pedido ao projeto certo",
                "executor": "pc_local_brain",
                "approval_required": False,
                "status": "planned",
            },
            {
                "step_id": "load-project-bootstrap-readiness",
                "label": "Ler readiness do Project Bootstrap Cockpit",
                "executor": "pc_local_brain",
                "approval_required": False,
                "status": "planned",
            },
        ]

        if intent in {"deep_project_audit", "repair_plan"}:
            steps.extend(
                [
                    {
                        "step_id": "map-related-repositories",
                        "label": "Mapear repos relacionados e papéis frontend/backend/site/cockpit",
                        "executor": "github_provider",
                        "approval_required": False,
                        "status": "planned",
                    },
                    {
                        "step_id": "scan-repo-files-and-dependencies",
                        "label": "Auditar ficheiros, imports, rotas, workflows e env vars esperadas",
                        "executor": "pc_local_brain",
                        "approval_required": False,
                        "status": "planned",
                    },
                    {
                        "step_id": "prepare-approval-gated-fix-plan",
                        "label": "Preparar plano de correção com PR limpa e pontos de aprovação",
                        "executor": "pc_local_brain",
                        "approval_required": True,
                        "status": "planned",
                    },
                ]
            )

        if intent == "multi_ai_conversation_mapping":
            steps.extend(
                [
                    {
                        "step_id": "inventory-ai-conversations",
                        "label": "Inventariar conversas multi-IA ligadas ao projeto",
                        "executor": "browser_provider_bridge",
                        "approval_required": True,
                        "status": "planned",
                    },
                    {
                        "step_id": "summarize-and-link-conversations",
                        "label": "Resumir conversas e ligar a projeto/repos",
                        "executor": "pc_local_brain",
                        "approval_required": False,
                        "status": "planned",
                    },
                ]
            )

        if intent == "deploy_or_build_readiness" or targets.get("needs_vault"):
            steps.extend(
                [
                    {
                        "step_id": "resolve-vault-secrets-for-project",
                        "label": "Resolver secrets/tokens do projeto no vault",
                        "executor": "secret_vault",
                        "approval_required": True,
                        "status": "planned",
                    },
                    {
                        "step_id": "validate-build-and-deploy-targets",
                        "label": "Validar GitHub Actions, artifacts, Vercel, Render e Supabase",
                        "executor": "provider_bridge",
                        "approval_required": False,
                        "status": "planned",
                    },
                ]
            )

        if command.get("destructive"):
            steps.append(
                {
                    "step_id": "hard-stop-destructive-action",
                    "label": "Bloquear ação destrutiva até aprovação explícita no cockpit mobile",
                    "executor": "mobile_approval_cockpit",
                    "approval_required": True,
                    "status": "blocked_until_operator_approval",
                }
            )

        steps.append(
            {
                "step_id": "report-back-to-mobile-cockpit",
                "label": "Enviar progresso, próximos passos e pedidos de aprovação ao telemóvel",
                "executor": "mobile_cockpit",
                "approval_required": False,
                "status": "planned",
            }
        )
        return steps

    def submit_command(
        self,
        command_text: str,
        tenant_id: str = "owner-andre",
        project_hint: str | None = None,
        source_channel: str = "mobile_chat",
    ) -> Dict[str, Any]:
        text = command_text.strip()
        if not text:
            return {"ok": False, "error": "command_text_empty"}

        project = self._guess_project(text, project_hint=project_hint)
        command_class = self._classify_intent(text)
        targets = self._extract_targets(text)
        command_id = f"cmd-{uuid4().hex[:12]}"
        created_at = self._now()

        bootstrap = project_bootstrap_cockpit_service.build_dashboard(
            tenant_id=tenant_id,
            project_name=project["project_name"],
            providers=["github", "vercel", "supabase", "render"],
            multirepo_mode=True,
        )

        command = {
            "command_id": command_id,
            "tenant_id": tenant_id,
            "source_channel": source_channel,
            "created_at": created_at,
            "raw_text": text,
            **command_class,
            "project": project,
            "targets": targets,
            "bootstrap_summary": {
                "launch_ready": bootstrap.get("launch_ready"),
                "readiness_score": bootstrap.get("readiness_score"),
                "blocker_count": bootstrap.get("blocker_count"),
            },
        }
        command["execution_plan"] = self._build_execution_plan(command, project, targets)

        memory = self._load_memory()
        project_record = memory["projects"].setdefault(
            project["project_id"],
            {
                "project_id": project["project_id"],
                "project_name": project["project_name"],
                "created_at": created_at,
                "last_seen_at": created_at,
                "command_ids": [],
                "known_repo_roles": [],
                "known_providers": [],
            },
        )
        project_record["project_name"] = project["project_name"]
        project_record["last_seen_at"] = created_at
        project_record["command_ids"].append(command_id)
        project_record["known_repo_roles"] = sorted(set(project_record.get("known_repo_roles", [])) | set(targets.get("repo_roles", [])))
        project_record["known_providers"] = sorted(set(project_record.get("known_providers", [])) | set(targets.get("providers", [])))
        memory["commands"].append(command)
        memory["commands"] = memory["commands"][-500:]
        self._save_memory(memory)

        return {
            "ok": True,
            "mode": "operator_command_intake_submit",
            "command": command,
            "project_memory": project_record,
        }

    def list_commands(
        self,
        tenant_id: str = "owner-andre",
        project_id: str | None = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        memory = self._load_memory()
        commands = [item for item in memory.get("commands", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            commands = [item for item in commands if item.get("project", {}).get("project_id") == project_id]
        commands = commands[-max(min(limit, 200), 1):]
        return {
            "ok": True,
            "mode": "operator_command_intake_list",
            "tenant_id": tenant_id,
            "project_id": project_id,
            "command_count": len(commands),
            "commands": commands,
        }

    def list_project_memory(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        memory = self._load_memory()
        projects = list(memory.get("projects", {}).values())
        return {
            "ok": True,
            "mode": "operator_command_intake_project_memory",
            "tenant_id": tenant_id,
            "project_count": len(projects),
            "projects": sorted(projects, key=lambda item: item.get("last_seen_at", ""), reverse=True),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_command_intake_package",
            "package": {
                "status": self.get_status(),
                "project_memory": self.list_project_memory(),
            },
        }


operator_command_intake_service = OperatorCommandIntakeService()
