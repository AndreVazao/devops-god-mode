from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


AGENT_ROLES: dict[str, dict[str, Any]] = {
    "architect": {
        "name": "Architect",
        "mission": "Definir arquitetura, fronteiras, módulos e decisões técnicas.",
        "handles": ["architecture", "design", "module_boundary", "technical_decision"],
        "tools": ["ecosystem_map", "andreos_memory", "obsidian_technical_sync", "goal_planner"],
        "outputs": ["architecture_note", "decision_record", "implementation_plan"],
        "risk_level": "medium",
    },
    "builder": {
        "name": "Builder",
        "mission": "Implementar alterações de código, serviços, rotas, UI e integrações.",
        "handles": ["feature", "bugfix", "implementation", "refactor"],
        "tools": ["github", "reusable_code_registry", "goal_planner"],
        "outputs": ["branch", "commit", "pull_request", "changed_files"],
        "risk_level": "medium",
    },
    "tester": {
        "name": "Tester",
        "mission": "Validar builds, smoke tests, regressões e endpoints críticos.",
        "handles": ["test", "validation", "workflow", "artifact", "smoke_test"],
        "tools": ["github_actions", "final_readiness", "real_operator_rehearsal"],
        "outputs": ["test_report", "workflow_result", "blocker_report"],
        "risk_level": "low",
    },
    "security": {
        "name": "Security Guard",
        "mission": "Proteger segredos, permissões, handoffs IA e ações perigosas.",
        "handles": ["security", "secret", "token", "password", "prompt_injection", "destructive_action"],
        "tools": ["ai_handoff_security_guard", "ai_handoff_trace", "permission_policy"],
        "outputs": ["risk_report", "sanitized_context", "approval_blocker"],
        "risk_level": "critical",
    },
    "memory": {
        "name": "Memory Curator",
        "mission": "Organizar GitHub memory, Obsidian, AndreOS e reconciliação de contexto.",
        "handles": ["memory", "obsidian", "andreos", "context", "history", "sync"],
        "tools": ["memory_boundary", "obsidian_technical_sync", "andreos_context", "andreos_memory_repo"],
        "outputs": ["memory_delta", "obsidian_note", "github_memory_update", "context_pack"],
        "risk_level": "medium",
    },
    "reusable_code": {
        "name": "Reusable Code Curator",
        "mission": "Encontrar, registar e adaptar código reutilizável antes de criar código novo.",
        "handles": ["reusable", "component", "pattern", "template", "library", "previous_code"],
        "tools": ["reusable_code_registry", "ecosystem_map"],
        "outputs": ["candidate_assets", "reuse_decision", "asset_registration"],
        "risk_level": "low",
    },
    "github": {
        "name": "GitHub Operator",
        "mission": "Gerir repos, branches, PRs, commits e workflows.",
        "handles": ["github", "repo", "branch", "pull_request", "commit", "workflow"],
        "tools": ["github", "build_control", "artifact_validation"],
        "outputs": ["branch", "commit", "pr", "merge_report"],
        "risk_level": "high",
    },
    "obsidian": {
        "name": "Obsidian Operator",
        "mission": "Organizar notas locais, operação real e evolução local.",
        "handles": ["obsidian", "local_note", "local_operation", "usage_evolution"],
        "tools": ["program_obsidian_policy", "obsidian_technical_sync"],
        "outputs": ["local_note", "technical_sync_candidate"],
        "risk_level": "low",
    },
    "release": {
        "name": "Release Manager",
        "mission": "Preparar artifacts, versões, changelog, readiness e atualização.",
        "handles": ["release", "artifact", "exe", "apk", "update", "installer", "version"],
        "tools": ["desktop_self_update", "download_install_center", "final_install_readiness", "github_actions"],
        "outputs": ["release_note", "artifact_links", "install_readiness_report"],
        "risk_level": "medium",
    },
    "mobile": {
        "name": "Mobile Operator",
        "mission": "Gerir APK, WebView mobile, pairing, ADB e experiência do telemóvel.",
        "handles": ["mobile", "android", "apk", "adb", "phone", "pairing", "overlay"],
        "tools": ["download_install_center", "mobile_pairing", "android_build"],
        "outputs": ["apk_status", "pairing_report", "mobile_test_plan"],
        "risk_level": "medium",
    },
    "desktop": {
        "name": "Desktop Operator",
        "mission": "Gerir EXE, backend local, Windows, firewall, health e logs.",
        "handles": ["desktop", "windows", "exe", "backend", "health", "firewall", "localhost"],
        "tools": ["desktop_self_update", "windows_exe_build", "health_check"],
        "outputs": ["desktop_status", "backend_health", "diagnostic_report"],
        "risk_level": "medium",
    },
    "ai_research": {
        "name": "AI Research Analyst",
        "mission": "Estudar Ruflo/outros projetos e extrair ideias úteis sem acoplamento perigoso.",
        "handles": ["ruflo", "research", "mcp", "swarm", "provider_router", "federation"],
        "tools": ["ruflo_research_lab", "reusable_code_registry", "ecosystem_map"],
        "outputs": ["research_mapping", "extraction_plan", "native_implementation_recommendation"],
        "risk_level": "low",
    },
}

TAG_TO_ROLES: dict[str, list[str]] = {
    "bugfix": ["tester", "builder", "github"],
    "feature": ["architect", "reusable_code", "builder", "tester"],
    "build_release": ["release", "tester", "github"],
    "memory": ["memory", "obsidian", "github"],
    "ai_orchestration": ["ai_research", "security", "architect", "builder"],
    "security": ["security", "tester"],
    "general_execution": ["architect", "builder", "tester"],
}


class AgentRolesRegistryService:
    """Registry and assignment logic for internal God Mode agent roles."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "agent_roles_registry",
            "created_at": _utc_now(),
            "role_count": len(AGENT_ROLES),
            "mode": "native_god_mode_agent_roles",
            "dependency_policy": "inspired_by_ruflo_but_no_runtime_dependency",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Agent Roles Registry",
            "description": "Catálogo de papéis internos do God Mode para atribuir tarefas a especialistas: architect, builder, tester, security, memory, release, mobile, desktop e outros.",
            "primary_actions": [
                {"label": "Listar roles", "endpoint": "/api/agent-roles/roles", "method": "GET", "safe": True},
                {"label": "Atribuir roles", "endpoint": "/api/agent-roles/assign", "method": "POST", "safe": True},
                {"label": "Plano de execução por roles", "endpoint": "/api/agent-roles/execution-plan", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "O God Mode deve escolher papéis internos antes de executar trabalho complexo.",
            "Security entra sempre que houver IA externa, tokens, cookies, passwords, prompt injection ou ação destrutiva.",
            "Reusable Code entra antes de criar código novo.",
            "Tester entra antes de merge/release/artifact.",
            "Memory entra quando houver GitHub memory, Obsidian, AndreOS ou contexto persistente.",
            "Release entra quando houver APK, EXE, artifact, update ou instalador.",
            "Papéis orientam execução; não são processos separados obrigatórios nesta fase.",
        ]

    def roles(self) -> dict[str, Any]:
        return {"ok": True, "roles": AGENT_ROLES}

    def get_role(self, role_id: str) -> dict[str, Any]:
        role = AGENT_ROLES.get(role_id)
        if not role:
            return {"ok": False, "error_type": "role_not_found", "role_id": role_id}
        return {"ok": True, "role_id": role_id, "role": role}

    def assign(
        self,
        goal: str,
        tags: list[str] | None = None,
        project: str | None = None,
        repo: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        inferred_tags = self._infer_tags(goal=goal, context=context, tags=tags)
        ordered_role_ids = self._roles_for_tags(inferred_tags, goal=goal, context=context, repo=repo)
        assignments = []
        for index, role_id in enumerate(ordered_role_ids, start=1):
            role = AGENT_ROLES[role_id]
            assignments.append(
                {
                    "order": index,
                    "role_id": role_id,
                    "name": role["name"],
                    "mission": role["mission"],
                    "risk_level": role["risk_level"],
                    "tools": role["tools"],
                    "expected_outputs": role["outputs"],
                    "why": self._why_role(role_id, inferred_tags, goal, context),
                }
            )
        return {
            "ok": True,
            "goal": goal,
            "project": project,
            "repo": repo,
            "tags": inferred_tags,
            "assignment_count": len(assignments),
            "assignments": assignments,
            "requires_security_first": assignments[0]["role_id"] == "security" if assignments else False,
        }

    def execution_plan(
        self,
        goal: str,
        tags: list[str] | None = None,
        project: str | None = None,
        repo: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        assignment = self.assign(goal=goal, tags=tags, project=project, repo=repo, context=context)
        steps = []
        for item in assignment.get("assignments", []):
            role_id = item["role_id"]
            steps.append(
                {
                    "step_id": f"AR{item['order']}",
                    "role_id": role_id,
                    "title": f"{item['name']} — {self._step_title(role_id)}",
                    "safe": role_id not in {"github", "builder", "release"} or "security" in assignment.get("tags", []),
                    "tools": item["tools"],
                    "outputs": item["expected_outputs"],
                }
            )
        return {
            "ok": True,
            "goal": goal,
            "project": project,
            "repo": repo,
            "tags": assignment.get("tags", []),
            "steps": steps,
            "next_role": steps[0] if steps else None,
            "operator_summary": self._summary(assignment, steps),
        }

    def _infer_tags(self, goal: str, context: str | None, tags: list[str] | None) -> list[str]:
        if tags:
            return list(dict.fromkeys(tags))
        text = f"{goal}\n{context or ''}".lower()
        inferred: list[str] = []
        if any(word in text for word in ["bug", "erro", "falha", "crash", "não abre", "nao abre"]):
            inferred.append("bugfix")
        if any(word in text for word in ["implementar", "adicionar", "criar", "nova função", "feature", "incremento", "avança"]):
            inferred.append("feature")
        if any(word in text for word in ["workflow", "build", "artifact", "apk", "exe", "release", "update"]):
            inferred.append("build_release")
        if any(word in text for word in ["memória", "memoria", "obsidian", "andreos", "contexto"]):
            inferred.append("memory")
        if any(word in text for word in ["ia", "chatgpt", "gemini", "deepseek", "grok", "ollama", "provider", "ruflo", "mcp"]):
            inferred.append("ai_orchestration")
        if any(word in text for word in ["segurança", "seguranca", "token", "password", "secret", "cookie", "prompt injection"]):
            inferred.append("security")
        return inferred or ["general_execution"]

    def _roles_for_tags(self, tags: list[str], goal: str, context: str | None, repo: str | None) -> list[str]:
        role_ids: list[str] = []
        for tag in tags:
            for role_id in TAG_TO_ROLES.get(tag, []):
                if role_id not in role_ids:
                    role_ids.append(role_id)
        text = f"{goal}\n{context or ''}".lower()
        if repo and "github" not in role_ids:
            role_ids.append("github")
        if any(word in text for word in ["apk", "android", "telemóvel", "telefone", "mobile"]):
            role_ids.append("mobile")
        if any(word in text for word in ["exe", "windows", "pc", "desktop", "localhost", "health"]):
            role_ids.append("desktop")
        if any(word in text for word in ["token", "password", "cookie", "secret", "apagar", "delete"]):
            if "security" in role_ids:
                role_ids.remove("security")
            role_ids.insert(0, "security")
        return list(dict.fromkeys(role_ids))

    def _why_role(self, role_id: str, tags: list[str], goal: str, context: str | None) -> str:
        role = AGENT_ROLES[role_id]
        matching = [tag for tag in tags if any(tag in handle or handle in tag for handle in role.get("handles", []))]
        if matching:
            return f"Relacionado com tags: {', '.join(matching)}."
        return "Selecionado por heurística do objetivo/contexto."

    def _step_title(self, role_id: str) -> str:
        titles = {
            "architect": "definir abordagem",
            "builder": "implementar alteração",
            "tester": "validar resultado",
            "security": "validar segurança",
            "memory": "preparar memória/contexto",
            "reusable_code": "procurar reaproveitamento",
            "github": "gerir branch/PR",
            "obsidian": "organizar nota local",
            "release": "preparar artifact/update",
            "mobile": "validar APK/telefone",
            "desktop": "validar EXE/backend PC",
            "ai_research": "estudar/adaptar referência IA",
        }
        return titles.get(role_id, "executar papel")

    def _summary(self, assignment: dict[str, Any], steps: list[dict[str, Any]]) -> str:
        roles = ", ".join(item["role_id"] for item in assignment.get("assignments", []))
        return f"Plano por roles criado com {len(steps)} passos. Roles: {roles}."

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "roles": AGENT_ROLES,
            "tag_to_roles": TAG_TO_ROLES,
        }


agent_roles_registry_service = AgentRolesRegistryService()
