from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


MCP_TOOL_CATALOG: dict[str, dict[str, Any]] = {
    "godmode.goal_planner.plan": {
        "title": "Create Goal Plan",
        "endpoint": "/api/goal-planner/plan",
        "method": "POST",
        "risk": "low",
        "category": "planning",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Transforma um objetivo em plano executável com tarefas, riscos, memória e validação.",
        "input_schema": {
            "goal": "string required",
            "project": "string optional",
            "repo": "string optional",
            "context": "string optional",
            "priority": "normal|high|critical optional",
            "execution_mode": "plan_only|safe_autopilot|needs_approval optional",
            "constraints": "array<string> optional",
        },
    },
    "godmode.agent_roles.assign": {
        "title": "Assign Agent Roles",
        "endpoint": "/api/agent-roles/assign",
        "method": "POST",
        "risk": "low",
        "category": "planning",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Atribui papéis internos do God Mode a um objetivo/tarefa.",
        "input_schema": {"goal": "string required", "tags": "array<string> optional", "project": "string optional", "repo": "string optional", "context": "string optional"},
    },
    "godmode.provider_router.route": {
        "title": "Route AI Provider",
        "endpoint": "/api/ai-provider-router/route",
        "method": "POST",
        "risk": "low",
        "category": "ai",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Escolhe provider IA e fallback por tarefa, sensibilidade e disponibilidade.",
        "input_schema": {
            "goal": "string required",
            "task_tags": "array<string> optional",
            "context": "string optional",
            "sensitive": "boolean optional",
            "needs_code": "boolean optional",
            "needs_large_context": "boolean optional",
            "needs_multimodal": "boolean optional",
            "primary_failed": "boolean optional",
            "provider_availability": "object optional",
            "preferred_provider": "string optional",
        },
    },
    "godmode.security.prepare_ai_handoff": {
        "title": "Prepare Secure AI Handoff",
        "endpoint": "/api/ai-handoff-security-guard/prepare",
        "method": "POST",
        "risk": "medium",
        "category": "security",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Analisa/sanitiza contexto e cria pacote seguro antes de enviar a IA.",
        "input_schema": {"text": "string required", "provider": "string optional", "purpose": "string optional", "project": "string optional", "repo": "string optional", "include_original": "boolean optional"},
        "hard_rules": ["include_original=false para providers externos", "não enviar secrets brutos"],
    },
    "godmode.reusable_code.search": {
        "title": "Search Reusable Code",
        "endpoint": "/api/reusable-code-registry/search",
        "method": "POST",
        "risk": "low",
        "category": "memory",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Pesquisa componentes/código reutilizável antes de criar código novo.",
        "input_schema": {"query": "string required", "project": "string optional", "limit": "integer optional"},
    },
    "godmode.ecosystem.classify": {
        "title": "Classify Ecosystem Project",
        "endpoint": "/api/ecosystem-map/classify",
        "method": "POST",
        "risk": "low",
        "category": "ecosystem",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Classifica projeto/repo por grupo, tipo de execução, memória e licenciamento provável.",
        "input_schema": {"name": "string required", "description": "string optional", "repo": "string optional", "is_cloud": "boolean optional", "is_mobile": "boolean optional"},
    },
    "godmode.andreos.context_panel": {
        "title": "AndreOS Context Panel",
        "endpoint": "/api/andreos-context/panel",
        "method": "GET/POST",
        "risk": "low",
        "category": "memory",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Obtém painel/orientação de contexto AndreOS.",
        "input_schema": {},
    },
    "godmode.obsidian.prepare_sync": {
        "title": "Prepare Obsidian Technical Sync",
        "endpoint": "/api/obsidian-technical-sync/prepare-sync",
        "method": "POST",
        "risk": "medium",
        "category": "memory",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": True,
        "description": "Prepara delta técnico de nota Obsidian para GitHub memory.",
        "input_schema": {"project": "string required", "note_title": "string required", "note_content": "string required", "source_path": "string optional"},
    },
    "godmode.ruflo.mapping": {
        "title": "Ruflo Research Mapping",
        "endpoint": "/api/ruflo-research-lab/mapping",
        "method": "GET/POST",
        "risk": "low",
        "category": "research",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Mostra mapa Ruflo → God Mode para extração de ideias úteis.",
        "input_schema": {},
    },
    "godmode.home.health": {
        "title": "Home Health Status",
        "endpoint": "/api/home-system-health/status",
        "method": "GET/POST",
        "risk": "low",
        "category": "diagnostics",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Consulta estado geral de saúde do God Mode.",
        "input_schema": {},
    },
    "godmode.release.final_readiness": {
        "title": "Final Install Readiness",
        "endpoint": "/api/final-install-readiness-v2/check",
        "method": "GET/POST",
        "risk": "low",
        "category": "release",
        "ai_callable": True,
        "requires_operator_approval": False,
        "requires_security_guard": False,
        "description": "Verifica prontidão para instalação/teste real.",
        "input_schema": {},
    },
}

RISK_RULES = {
    "low": "Leitura, planeamento, classificação ou análise sem alteração destrutiva.",
    "medium": "Pode preparar alterações, syncs ou contexto sensível; exige guardrails.",
    "high": "Pode alterar repo, memória estável, update ou release; exige aprovação clara.",
    "critical": "Ação destrutiva, credenciais, pagamentos, licenças ou eliminação; bloqueado sem aprovação explícita do Oner.",
}


class McpCompatibilityMapService:
    """Maps internal God Mode endpoints into future MCP-compatible tools."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "mcp_compatibility_map",
            "created_at": _utc_now(),
            "tool_count": len(MCP_TOOL_CATALOG),
            "mode": "compatibility_map_only",
            "runtime_mcp_server": False,
            "dependency_policy": "no_mcp_dependency_yet",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "MCP Compatibility Map",
            "description": "Mapa dos endpoints do God Mode que podem virar tools MCP/agents no futuro, com risco, schema e permissões.",
            "primary_actions": [
                {"label": "Listar tools", "endpoint": "/api/mcp-compatibility/tools", "method": "GET", "safe": True},
                {"label": "Exportar manifest", "endpoint": "/api/mcp-compatibility/manifest", "method": "GET", "safe": True},
                {"label": "Validar tool", "endpoint": "/api/mcp-compatibility/validate-tool", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Esta fase não cria servidor MCP real; cria mapa de compatibilidade seguro.",
            "Tools de risco low podem ser chamadas por IA para leitura/planeamento.",
            "Tools medium exigem Security Guard quando lidam com contexto sensível.",
            "Tools high/critical exigem aprovação explícita do Oner antes de execução real.",
            "Nenhuma tool MCP pode receber ou devolver secrets brutos.",
            "O manifesto MCP deve expor schemas mínimos e não credenciais internas.",
            "A compatibilidade MCP deve respeitar Goal Planner, Agent Roles, Provider Router e AI Handoff Trace.",
        ]

    def tools(self, category: str | None = None, risk: str | None = None, ai_callable: bool | None = None) -> dict[str, Any]:
        results = {}
        for tool_id, tool in MCP_TOOL_CATALOG.items():
            if category and tool.get("category") != category:
                continue
            if risk and tool.get("risk") != risk:
                continue
            if ai_callable is not None and bool(tool.get("ai_callable")) is not ai_callable:
                continue
            results[tool_id] = tool
        return {"ok": True, "count": len(results), "tools": results}

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        tool = MCP_TOOL_CATALOG.get(tool_id)
        if not tool:
            return {"ok": False, "error_type": "tool_not_found", "tool_id": tool_id}
        return {"ok": True, "tool_id": tool_id, "tool": tool}

    def manifest(self, include_internal_notes: bool = False) -> dict[str, Any]:
        tools = []
        for tool_id, tool in MCP_TOOL_CATALOG.items():
            entry = {
                "name": tool_id,
                "title": tool["title"],
                "description": tool["description"],
                "input_schema": tool.get("input_schema", {}),
                "metadata": {
                    "endpoint": tool["endpoint"],
                    "method": tool["method"],
                    "risk": tool["risk"],
                    "category": tool["category"],
                    "requires_operator_approval": tool["requires_operator_approval"],
                    "requires_security_guard": tool["requires_security_guard"],
                },
            }
            if include_internal_notes:
                entry["internal_notes"] = {"ai_callable": tool.get("ai_callable"), "hard_rules": tool.get("hard_rules", [])}
            tools.append(entry)
        return {
            "ok": True,
            "manifest_version": "0.1-godmode-mcp-compatibility-map",
            "created_at": _utc_now(),
            "runtime_mcp_server": False,
            "tools": tools,
            "risk_rules": RISK_RULES,
        }

    def validate_tool_call(self, tool_id: str, payload: dict[str, Any] | None = None, operator_approved: bool = False) -> dict[str, Any]:
        tool = MCP_TOOL_CATALOG.get(tool_id)
        if not tool:
            return {"ok": False, "allowed": False, "error_type": "tool_not_found", "tool_id": tool_id}
        payload = payload or {}
        risk = tool["risk"]
        blockers = []
        if risk in {"high", "critical"} and not operator_approved:
            blockers.append("operator_approval_required")
        if tool.get("requires_security_guard"):
            blockers.append("security_guard_required_before_execution")
        if self._payload_has_secret_words(payload):
            blockers.append("payload_may_contain_secret_words")
        allowed = not blockers or blockers == ["security_guard_required_before_execution"]
        return {
            "ok": True,
            "tool_id": tool_id,
            "risk": risk,
            "allowed": allowed,
            "operator_approved": operator_approved,
            "blockers": blockers,
            "required_gates": self._required_gates(tool, risk, blockers),
            "recommendation": self._recommendation(tool, blockers),
        }

    def _payload_has_secret_words(self, payload: dict[str, Any]) -> bool:
        text = str(payload).lower()
        return any(word in text for word in ["token", "password", "senha", "cookie", "private_key", "api_key", "secret"])

    def _required_gates(self, tool: dict[str, Any], risk: str, blockers: list[str]) -> list[str]:
        gates = ["ai_handoff_trace"]
        if tool.get("requires_security_guard") or "payload_may_contain_secret_words" in blockers:
            gates.append("ai_handoff_security_guard")
        if risk in {"high", "critical"}:
            gates.append("operator_approval")
        return list(dict.fromkeys(gates))

    def _recommendation(self, tool: dict[str, Any], blockers: list[str]) -> str:
        if "operator_approval_required" in blockers:
            return "Pedir aprovação explícita do Oner antes de executar esta tool."
        if "payload_may_contain_secret_words" in blockers:
            return "Sanitizar payload com AI Handoff Security Guard antes de prosseguir."
        if "security_guard_required_before_execution" in blockers:
            return "Passar pelo Security Guard antes de executar ou expor o payload."
        return "Tool validada para uso seguro conforme risco declarado."

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "manifest": self.manifest(include_internal_notes=True),
        }


mcp_compatibility_map_service = McpCompatibilityMapService()
