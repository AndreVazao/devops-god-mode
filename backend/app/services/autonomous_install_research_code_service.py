from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_bootstrap_backup_service import local_bootstrap_backup_service
from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service
from app.services.memory_context_router_service import memory_context_router_service
from app.services.operator_priority_service import operator_priority_service
from app.services.provider_completion_router_service import provider_completion_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SERVICE_FILE = DATA_DIR / "autonomous_install_research_code.json"
SERVICE_STORE = AtomicJsonStore(
    SERVICE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "autonomous_install_research_and_code_delivery_with_safe_gates",
        "install_decisions": [],
        "research_plans": [],
        "research_notes": [],
        "provider_scores": {},
        "code_contracts": [],
        "delivery_runs": [],
    },
)


class AutonomousInstallResearchCodeService:
    """Autonomous setup, research and code delivery coordination.

    This layer keeps the operator mobile-first: safe actions run automatically,
    local tools are installed when policy says the PC can handle them, research
    plans gather useful project knowledge, and code work is structured into
    language-specific contracts.
    """

    PROVIDERS = [
        {"id": "chatgpt", "label": "ChatGPT", "role": "primary_daily", "default_rank": 1},
        {"id": "deepseek", "label": "DeepSeek", "role": "code_completion_fallback", "default_rank": 2},
        {"id": "claude", "label": "Claude", "role": "large_context_review", "default_rank": 3},
        {"id": "gemini", "label": "Gemini", "role": "multimodal_or_research", "default_rank": 4},
        {"id": "google_web", "label": "Google/Web", "role": "public_research", "default_rank": 5},
        {"id": "local_ai", "label": "Local AI", "role": "offline_private_drafts", "default_rank": 6},
    ]

    RESEARCH_SOURCES = [
        {"id": "google_web", "label": "Google/Web search", "use": "general_public_research"},
        {"id": "official_docs", "label": "Official docs", "use": "api_or_tool_truth"},
        {"id": "github", "label": "GitHub repositories/issues", "use": "code_patterns_and_errors"},
        {"id": "community_forums", "label": "Community forums", "use": "player_or_user_observations"},
        {"id": "provider_chat", "label": "AI provider chats", "use": "reasoning_and_code_iteration"},
        {"id": "local_memory", "label": "AndreOS/Obsidian memory", "use": "project_context_and_decisions"},
    ]

    LANGUAGE_STACKS = {
        "python": {"tools": ["python", "pip", "pytest", "ruff"], "use": "backend, automation, scripts"},
        "javascript": {"tools": ["node", "npm", "eslint"], "use": "frontend and browser automation"},
        "typescript": {"tools": ["node", "npm", "tsc"], "use": "frontend, dashboards, typed apps"},
        "kotlin": {"tools": ["gradle", "android_sdk"], "use": "android native"},
        "java": {"tools": ["gradle", "jdk"], "use": "android/backend"},
        "powershell": {"tools": ["powershell"], "use": "windows setup and automation"},
        "html_css": {"tools": ["browser", "node"], "use": "UI and static views"},
        "sql": {"tools": ["sqlite", "postgres"], "use": "database schema and migrations"},
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "autonomous_install_research_code_policy",
            "install_policy": {
                "auto_install_allowed": True,
                "rule": "instalar automaticamente ferramentas necessárias quando o PC for adequado e a ferramenta for confiável",
                "weak_pc_rule": "em PC fraco, instalar só ferramentas leves e preferir GitHub Actions/cloud para builds pesados",
                "strong_pc_rule": "em PC novo/forte, preparar toolchain completa quando possível",
                "still_stop_for": ["admin prompt do Windows", "licença externa", "login manual", "pagamento", "instalador desconhecido", "risco de sobrescrever dados"],
            },
            "login_policy": {
                "operator_logs_in_once": True,
                "god_mode_reuses_existing_browser_session": True,
                "do_not_store_secrets_in_memory": True,
                "credential_storage": "defer_to_browser_or_os_secure_store",
            },
            "research_policy": {
                "google_web_allowed": True,
                "use_public_sources_for_project_knowledge": True,
                "store_useful_summaries_by_project": True,
                "do_not_copy_private_or_sensitive_material": True,
                "prefer_official_sources_when_available": True,
            },
            "code_policy": {
                "god_mode_has_own_code_contracts": True,
                "generate_language_specific_plan": True,
                "validate_before_delivery": True,
                "keep_working_until_program_is_functional": True,
            },
        }

    def decide_auto_install(self, pc_profile: str = "auto") -> Dict[str, Any]:
        scan = local_tool_capability_scan_service.scan().get("scan", {})
        bootstrap_plan = local_bootstrap_backup_service.bootstrap_plan(pc_profile=pc_profile).get("plan", {})
        missing = bootstrap_plan.get("missing_tools") or []
        skipped = bootstrap_plan.get("skipped_tools") or []
        weak = bool(bootstrap_plan.get("weak_pc_detected"))
        decisions: List[Dict[str, Any]] = []
        for item in missing:
            light = bool(item.get("light_pc", True))
            priority = item.get("priority", "medium")
            can_auto = bool(item.get("winget")) and (light or not weak) and priority in {"critical", "high", "medium"}
            decisions.append({
                "tool_id": item.get("tool_id"),
                "label": item.get("label"),
                "decision": "auto_install_script_allowed" if can_auto else "manual_or_skip",
                "reason": self._install_reason(item, weak, can_auto),
                "winget": item.get("winget"),
                "priority": priority,
                "light_pc": light,
            })
        for item in skipped:
            decisions.append({
                "tool_id": item.get("tool_id"),
                "label": item.get("label"),
                "decision": "skip_on_this_pc",
                "reason": "PC fraco ou ferramenta pesada; usar alternativa cloud/GitHub Actions.",
                "priority": item.get("priority"),
                "light_pc": item.get("light_pc"),
            })
        script = local_bootstrap_backup_service.install_script(pc_profile=pc_profile)
        result = {
            "decision_id": f"auto-install-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "weak_pc_detected": weak,
            "scan_id": scan.get("scan_id"),
            "decisions": decisions,
            "install_script_path": script.get("script_path"),
            "can_run_without_manual_configuration": True,
            "operator_interruption_only_for": ["Windows admin prompt", "manual login", "unexpected installer failure"],
        }
        self._store("install_decisions", result)
        return {"ok": True, "mode": "autonomous_auto_install_decision", "decision": result}

    def _install_reason(self, item: Dict[str, Any], weak: bool, can_auto: bool) -> str:
        if can_auto:
            return "Ferramenta necessária, pacote conhecido e PC adequado para tentar instalar/configurar automaticamente."
        if weak and not item.get("light_pc", True):
            return "Ferramenta pesada para este PC; preferir alternativa cloud/GitHub Actions."
        if not item.get("winget"):
            return "Sem pacote winget conhecido; precisa caminho manual ou fase futura."
        return "Não cumpre política de auto-instalação para este perfil."

    def research_plan(
        self,
        project_id: Optional[str] = None,
        topic: str = "",
        objective: str = "recolher informação útil para desenvolvimento do projeto",
        include_google: bool = True,
        include_ai_providers: bool = True,
    ) -> Dict[str, Any]:
        project = self._resolve_project(project_id)
        context = memory_context_router_service.prepare_project_context(
            project_id=project,
            source="autonomous_research_plan",
            max_chars=8000,
        ).get("context_pack")
        queries = self._build_queries(project, topic, objective)
        sources = [source for source in self.RESEARCH_SOURCES if include_google or source["id"] != "google_web"]
        if not include_ai_providers:
            sources = [source for source in sources if source["id"] != "provider_chat"]
        plan = {
            "research_plan_id": f"research-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "topic": topic or project,
            "objective": objective,
            "context_pack_id": (context or {}).get("context_pack_id"),
            "queries": queries,
            "sources": sources,
            "store_results_to": f"memory/vault/AndreOS/02_PROJETOS/{project}/PESQUISA.md",
            "rules": [
                "preferir fontes oficiais quando existirem",
                "usar Google/Web para descobrir informação pública atual",
                "guardar resumo útil por projeto, não dumps gigantes",
                "se encontrar novidade relevante, criar item de backlog/update",
                "não guardar credenciais, cookies ou material privado",
            ],
            "next_actions": [
                {"label": "Pesquisar Web/Google", "source": "google_web"},
                {"label": "Consultar provider principal", "source": "chatgpt"},
                {"label": "Consultar fallback de código", "source": "deepseek"},
                {"label": "Atualizar memória do projeto", "source": "local_memory"},
            ],
        }
        self._store("research_plans", plan)
        return {"ok": True, "mode": "autonomous_research_plan", "plan": plan}

    def add_research_note(
        self,
        project_id: Optional[str] = None,
        source: str = "manual",
        title: str = "",
        summary: str = "",
        url: Optional[str] = None,
        usefulness_score: int = 70,
    ) -> Dict[str, Any]:
        project = self._resolve_project(project_id)
        note = {
            "note_id": f"research-note-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "source": source,
            "title": title[:300],
            "summary": summary[:5000],
            "url": url,
            "usefulness_score": max(0, min(100, usefulness_score)),
            "backlog_recommendation": self._backlog_recommendation(summary),
        }
        self._store("research_notes", note)
        return {"ok": True, "mode": "autonomous_research_note_added", "note": note}

    def code_contract(
        self,
        project_id: Optional[str] = None,
        goal: str = "entregar programa funcional",
        language: str = "auto",
        target_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        project = self._resolve_project(project_id)
        detected_language = self._detect_language(language, target_files or [])
        stack = self.LANGUAGE_STACKS.get(detected_language, {"tools": [], "use": "generic software delivery"})
        context = memory_context_router_service.prepare_project_context(
            project_id=project,
            source="autonomous_code_contract",
            max_chars=12000,
        ).get("context_pack")
        contract = {
            "contract_id": f"code-contract-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "goal": goal,
            "language": detected_language,
            "stack": stack,
            "target_files": target_files or [],
            "context_pack_id": (context or {}).get("context_pack_id"),
            "delivery_definition": [
                "perceber objetivo e estado atual",
                "propor arquitetura mínima funcional",
                "gerar ou alterar ficheiros completos",
                "validar imports/rotas/build quando possível",
                "guardar decisão e próxima ação na memória",
                "preparar PR/build/artifact quando aplicável",
            ],
            "validation_commands": self._validation_commands(detected_language),
            "provider_sequence": self._provider_sequence_for_code(detected_language),
            "done_when": [
                "código executável ou buildável",
                "sem placeholders críticos",
                "rotas/UI ligadas à Home/Modo Fácil quando aplicável",
                "memória atualizada",
                "próxima ação clara",
            ],
        }
        self._store("code_contracts", contract)
        return {"ok": True, "mode": "autonomous_code_contract", "contract": contract}

    def delivery_run(
        self,
        project_id: Optional[str] = None,
        goal: str = "continuar até produto funcional",
        topic: str = "",
        language: str = "auto",
        pc_profile: str = "auto",
    ) -> Dict[str, Any]:
        project = self._resolve_project(project_id)
        install = self.decide_auto_install(pc_profile=pc_profile).get("decision")
        research = self.research_plan(project_id=project, topic=topic or goal, objective=f"apoiar entrega: {goal}").get("plan")
        contract = self.code_contract(project_id=project, goal=goal, language=language).get("contract")
        provider_plan = provider_completion_router_service.completion_plan(
            provider_id="chatgpt",
            project_id=project,
            event_text="delivery run requested by operator",
            failure_type="unknown",
            final_objective=goal,
        ).get("plan")
        run = {
            "run_id": f"delivery-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "goal": goal,
            "status": "ready_to_execute_autonomous_workflow",
            "install_decision_id": install.get("decision_id") if install else None,
            "research_plan_id": research.get("research_plan_id") if research else None,
            "code_contract_id": contract.get("contract_id") if contract else None,
            "provider_completion_plan_id": provider_plan.get("plan_id") if provider_plan else None,
            "autonomy": {
                "can_research_without_operator": True,
                "can_generate_code_without_operator": True,
                "can_prepare_files_without_operator": True,
                "can_install_known_tools_if_pc_ok": True,
                "stops_for_login_or_destructive_actions": True,
            },
            "next": [
                {"label": "Executar pesquisa pública", "endpoint": "/api/autonomous-delivery/research-plan"},
                {"label": "Gerar contrato de código", "endpoint": "/api/autonomous-delivery/code-contract"},
                {"label": "Atualizar memória", "endpoint": "/api/memory-context-router/prepare-project"},
                {"label": "Preparar PR/build", "endpoint": "/api/daily-command-router/route"},
            ],
        }
        self._store("delivery_runs", run)
        return {"ok": True, "mode": "autonomous_delivery_run", "run": run}

    def provider_score(self, provider_id: str, success: bool, reason: str = "", project_id: Optional[str] = None) -> Dict[str, Any]:
        project = self._resolve_project(project_id)
        state = SERVICE_STORE.load()
        scores = state.setdefault("provider_scores", {})
        key = provider_id.lower().strip() or "unknown"
        current = scores.get(key, {"provider_id": key, "successes": 0, "failures": 0, "score": 50, "events": []})
        if success:
            current["successes"] = current.get("successes", 0) + 1
        else:
            current["failures"] = current.get("failures", 0) + 1
        total = current["successes"] + current["failures"]
        current["score"] = round((current["successes"] / total) * 100) if total else 50
        current.setdefault("events", []).append({"created_at": self._now(), "project_id": project, "success": success, "reason": reason[:500]})
        current["events"] = current["events"][-50:]
        scores[key] = current
        SERVICE_STORE.save(state)
        return {"ok": True, "mode": "autonomous_provider_score", "score": current}

    def _build_queries(self, project: str, topic: str, objective: str) -> List[Dict[str, Any]]:
        base = topic.strip() or project.replace("_", " ")
        return [
            {"id": "official", "query": f"{base} official documentation updates", "priority": "high"},
            {"id": "community", "query": f"{base} community guide tips changes", "priority": "medium"},
            {"id": "github", "query": f"{base} GitHub implementation examples issues", "priority": "medium"},
            {"id": "objective", "query": f"{base} {objective}", "priority": "high"},
        ]

    def _resolve_project(self, project_id: Optional[str]) -> str:
        if project_id:
            return project_id.strip().upper().replace("-", "_").replace(" ", "_") or "GOD_MODE"
        priorities = operator_priority_service.get_status()
        return priorities.get("active_project") or "GOD_MODE"

    def _backlog_recommendation(self, summary: str) -> Dict[str, Any]:
        text = summary.lower()
        if any(word in text for word in ["update", "novo", "changed", "alterou", "mudou", "feature"]):
            return {"create_backlog_item": True, "reason": "possible_new_feature_or_change"}
        return {"create_backlog_item": False, "reason": "reference_note_only"}

    def _detect_language(self, language: str, target_files: List[str]) -> str:
        if language and language != "auto":
            return language.lower().replace(" ", "_")
        joined = " ".join(target_files).lower()
        if ".py" in joined:
            return "python"
        if ".tsx" in joined or ".ts" in joined:
            return "typescript"
        if ".jsx" in joined or ".js" in joined:
            return "javascript"
        if ".kt" in joined:
            return "kotlin"
        if ".java" in joined:
            return "java"
        if ".ps1" in joined:
            return "powershell"
        if ".sql" in joined:
            return "sql"
        if ".html" in joined or ".css" in joined:
            return "html_css"
        return "python"

    def _validation_commands(self, language: str) -> List[str]:
        mapping = {
            "python": ["python -m compileall backend", "pytest -q"],
            "typescript": ["npm run typecheck", "npm test"],
            "javascript": ["npm test"],
            "kotlin": ["./gradlew assembleDebug"],
            "java": ["./gradlew test"],
            "powershell": ["powershell -NoProfile -ExecutionPolicy Bypass -File <script>.ps1 -WhatIf"],
            "sql": ["run migration dry-run"],
            "html_css": ["npm run build"],
        }
        return mapping.get(language, ["project specific validation"])

    def _provider_sequence_for_code(self, language: str) -> List[Dict[str, Any]]:
        sequence = [
            {"provider_id": "chatgpt", "role": "primary implementation"},
            {"provider_id": "deepseek", "role": "code completion fallback"},
            {"provider_id": "claude", "role": "large context review"},
            {"provider_id": "local_ai", "role": "offline draft/support"},
        ]
        if language in {"kotlin", "java"}:
            sequence.insert(2, {"provider_id": "google_web", "role": "android docs and errors"})
        return sequence

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-200:]
            return state
        SERVICE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = SERVICE_STORE.load()
        return {
            "ok": True,
            "mode": "autonomous_install_research_code_latest",
            "latest_install_decision": (state.get("install_decisions") or [None])[-1],
            "latest_research_plan": (state.get("research_plans") or [None])[-1],
            "latest_research_note": (state.get("research_notes") or [None])[-1],
            "latest_code_contract": (state.get("code_contracts") or [None])[-1],
            "latest_delivery_run": (state.get("delivery_runs") or [None])[-1],
            "provider_scores": state.get("provider_scores", {}),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "autonomous_delivery_panel",
            "headline": "Entrega automática: instalar, pesquisar e gerar código",
            "policy": self.policy(),
            "providers": self.PROVIDERS,
            "research_sources": self.RESEARCH_SOURCES,
            "language_stacks": self.LANGUAGE_STACKS,
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "auto_install", "label": "Decidir/instalar ferramentas", "endpoint": "/api/autonomous-delivery/auto-install-decision", "priority": "critical"},
                {"id": "research", "label": "Pesquisar informação", "endpoint": "/api/autonomous-delivery/research-plan", "priority": "critical"},
                {"id": "code", "label": "Contrato de código", "endpoint": "/api/autonomous-delivery/code-contract", "priority": "critical"},
                {"id": "run", "label": "Executar entrega", "endpoint": "/api/autonomous-delivery/run", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "autonomous_install_research_code_status",
            "auto_install_allowed": True,
            "google_web_research_allowed": True,
            "own_code_contracts_enabled": True,
            "provider_scoring_enabled": True,
            "has_delivery_run": latest.get("latest_delivery_run") is not None,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "autonomous_install_research_code_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


autonomous_install_research_code_service = AutonomousInstallResearchCodeService()
