from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.operator_command_intake_service import operator_command_intake_service

DATA_DIR = Path("data")
INVENTORY_FILE = DATA_DIR / "multi_ai_conversation_inventory.json"

SUPPORTED_PROVIDERS = ["chatgpt", "claude", "gemini", "grok", "deepseek", "unknown"]
PROJECT_KEYWORDS = {
    "baribudos-studio": ["baribudos", "bodybou", "very good", "studio", "website"],
    "devops-god-mode": ["god mode", "godmode", "ai da box", "cockpit", "multi-ai", "multi ia"],
    "botfarm-headless": ["botfarm", "bot farm", "headless", "lords mobile", "farm"],
    "proventil": ["proventil", "video porteiro", "ventilação", "fumos"],
}


class MultiAIConversationInventoryService:
    """Inventory and mapping layer for conversations from multiple AI providers.

    This phase does not scrape private provider accounts by itself. It creates the
    local-first inventory model that later browser/session providers can feed.
    The operator can seed captured snippets now and the God Mode can map them to
    projects, repo roles and pending next actions.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "multi_ai_conversation_inventory_status",
            "status": "multi_ai_conversation_inventory_ready",
            "supported_providers": SUPPORTED_PROVIDERS,
            "inventory_file": str(INVENTORY_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_inventory(self) -> Dict[str, Any]:
        if not INVENTORY_FILE.exists():
            return {"conversations": [], "project_map": {}}
        try:
            loaded = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"conversations": [], "project_map": {}}
            loaded.setdefault("conversations", [])
            loaded.setdefault("project_map", {})
            return loaded
        except json.JSONDecodeError:
            return {"conversations": [], "project_map": {}}

    def _save_inventory(self, inventory: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        INVENTORY_FILE.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized or "conversation-project"

    def _normalize_provider(self, provider: str | None) -> str:
        normalized = (provider or "unknown").lower().strip()
        aliases = {
            "chat gpt": "chatgpt",
            "openai": "chatgpt",
            "google gemini": "gemini",
            "bard": "gemini",
            "xai": "grok",
            "deep seek": "deepseek",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in SUPPORTED_PROVIDERS else "unknown"

    def _guess_project(self, text: str, project_hint: str | None = None) -> Dict[str, Any]:
        if project_hint and project_hint.strip():
            name = project_hint.strip()
            return {"project_id": self._slugify(name), "project_name": name, "confidence": 0.95}
        lowered = text.lower()
        best_project = "general-intake"
        best_score = 0
        for project_id, keywords in PROJECT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_score = score
                best_project = project_id
        confidence = min(0.35 + best_score * 0.18, 0.92) if best_score else 0.25
        return {"project_id": best_project, "project_name": best_project.replace("-", " ").title(), "confidence": confidence}

    def _extract_repo_roles(self, text: str) -> List[str]:
        lowered = text.lower()
        roles: List[str] = []
        role_terms = {
            "website": ["website", "site", "landing"],
            "studio": ["studio", "cockpit", "dashboard"],
            "backend": ["backend", "back end", "api", "fastapi", "server"],
            "frontend": ["frontend", "front end", "react", "next", "ui"],
            "mobile": ["mobile", "telemóvel", "android", "apk"],
            "workflow": ["workflow", "github actions", "build", "artifact", "artefact"],
            "vault": ["vault", "secret", "token", "key", "chave"],
        }
        for role, terms in role_terms.items():
            if any(term in lowered for term in terms):
                roles.append(role)
        return sorted(set(roles))

    def _extract_languages(self, text: str) -> List[str]:
        lowered = text.lower()
        languages = []
        for language in ["python", "typescript", "javascript", "kotlin", "java", "swift", "sql", "html", "css", "yaml"]:
            if language in lowered:
                languages.append(language)
        if "fastapi" in lowered:
            languages.append("python")
        if "next.js" in lowered or "nextjs" in lowered:
            languages.append("typescript")
        return sorted(set(languages))

    def _summarize(self, title: str, snippet: str) -> str:
        base = (snippet or title).strip().replace("\n", " ")
        base = re.sub(r"\s+", " ", base)
        if len(base) > 240:
            return base[:237].rstrip() + "..."
        return base or "Sem resumo disponível."

    def stage_conversation(
        self,
        provider: str,
        title: str,
        snippet: str = "",
        conversation_url: str | None = None,
        project_hint: str | None = None,
        tenant_id: str = "owner-andre",
        source_status: str = "manual_seed",
    ) -> Dict[str, Any]:
        provider_name = self._normalize_provider(provider)
        text = f"{title}\n{snippet}"
        project = self._guess_project(text, project_hint=project_hint)
        conversation_id = f"conv-{uuid4().hex[:12]}"
        created_at = self._now()
        record = {
            "conversation_id": conversation_id,
            "tenant_id": tenant_id,
            "provider": provider_name,
            "title": title.strip() or "Untitled conversation",
            "snippet": snippet.strip(),
            "summary": self._summarize(title, snippet),
            "conversation_url": conversation_url,
            "source_status": source_status,
            "created_at": created_at,
            "updated_at": created_at,
            "project": project,
            "repo_roles": self._extract_repo_roles(text),
            "languages": self._extract_languages(text),
            "mapping_status": "mapped" if project["project_id"] != "general-intake" else "needs_review",
        }

        inventory = self._load_inventory()
        inventory["conversations"].append(record)
        project_entry = inventory["project_map"].setdefault(
            project["project_id"],
            {
                "project_id": project["project_id"],
                "project_name": project["project_name"],
                "conversation_ids": [],
                "providers": [],
                "repo_roles": [],
                "languages": [],
                "last_seen_at": created_at,
            },
        )
        project_entry["project_name"] = project["project_name"]
        project_entry["conversation_ids"].append(conversation_id)
        project_entry["providers"] = sorted(set(project_entry.get("providers", [])) | {provider_name})
        project_entry["repo_roles"] = sorted(set(project_entry.get("repo_roles", [])) | set(record["repo_roles"]))
        project_entry["languages"] = sorted(set(project_entry.get("languages", [])) | set(record["languages"]))
        project_entry["last_seen_at"] = created_at
        self._save_inventory(inventory)

        return {"ok": True, "mode": "multi_ai_conversation_stage", "conversation": record, "project_entry": project_entry}

    def seed_from_operator_command(
        self,
        command_id: str | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        commands = operator_command_intake_service.list_commands(tenant_id=tenant_id, limit=100).get("commands", [])
        if command_id:
            commands = [item for item in commands if item.get("command_id") == command_id]
        if not commands:
            return {"ok": False, "error": "operator_command_not_found", "command_id": command_id}
        command = commands[-1]
        project_name = command.get("project", {}).get("project_name", "general-intake")
        staged = self.stage_conversation(
            provider="unknown",
            title=f"Operator command: {command.get('intent', 'general')}",
            snippet=command.get("raw_text", ""),
            conversation_url=None,
            project_hint=project_name,
            tenant_id=tenant_id,
            source_status="operator_command_seed",
        )
        return {"ok": True, "mode": "multi_ai_seed_from_operator_command", "source_command": command, "staged": staged}

    def list_conversations(
        self,
        tenant_id: str = "owner-andre",
        project_id: str | None = None,
        provider: str | None = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        inventory = self._load_inventory()
        conversations = [item for item in inventory.get("conversations", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            conversations = [item for item in conversations if item.get("project", {}).get("project_id") == project_id]
        if provider:
            provider_name = self._normalize_provider(provider)
            conversations = [item for item in conversations if item.get("provider") == provider_name]
        conversations = conversations[-max(min(limit, 500), 1):]
        return {
            "ok": True,
            "mode": "multi_ai_conversation_list",
            "tenant_id": tenant_id,
            "project_id": project_id,
            "provider": provider,
            "conversation_count": len(conversations),
            "conversations": conversations,
        }

    def build_project_map(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        inventory = self._load_inventory()
        project_map = list(inventory.get("project_map", {}).values())
        project_map = sorted(project_map, key=lambda item: item.get("last_seen_at", ""), reverse=True)
        return {
            "ok": True,
            "mode": "multi_ai_project_map",
            "tenant_id": tenant_id,
            "project_count": len(project_map),
            "projects": project_map,
        }

    def build_inventory_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        inventory = self._load_inventory()
        conversations = [item for item in inventory.get("conversations", []) if item.get("tenant_id") == tenant_id]
        provider_counts: Dict[str, int] = {}
        needs_review = 0
        for item in conversations:
            provider_counts[item.get("provider", "unknown")] = provider_counts.get(item.get("provider", "unknown"), 0) + 1
            if item.get("mapping_status") != "mapped":
                needs_review += 1
        return {
            "ok": True,
            "mode": "multi_ai_conversation_inventory_dashboard",
            "tenant_id": tenant_id,
            "conversation_count": len(conversations),
            "project_count": len(inventory.get("project_map", {})),
            "provider_counts": provider_counts,
            "needs_review_count": needs_review,
            "projects": self.build_project_map(tenant_id=tenant_id).get("projects", []),
            "recent_conversations": conversations[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "multi_ai_conversation_inventory_package",
            "package": {
                "status": self.get_status(),
                "dashboard": self.build_inventory_dashboard(),
            },
        }


multi_ai_conversation_inventory_service = MultiAIConversationInventoryService()
