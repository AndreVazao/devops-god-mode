from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.multi_ai_conversation_inventory_service import multi_ai_conversation_inventory_service
from app.services.operator_command_intake_service import operator_command_intake_service

DATA_DIR = Path("data")
REPO_GRAPH_FILE = DATA_DIR / "repo_relationship_graph.json"

ROLE_HINTS = {
    "website": ["website", "site", "landing", "web"],
    "studio": ["studio", "cockpit", "dashboard", "admin"],
    "backend": ["backend", "api", "server", "fastapi", "render"],
    "frontend": ["frontend", "react", "next", "ui", "vercel"],
    "mobile": ["mobile", "android", "apk", "phone"],
    "workflow": ["workflow", "actions", "build", "artifact", "ci"],
    "vault": ["vault", "secret", "token", "env", "supabase"],
}


class RepoRelationshipGraphService:
    """Project/repository graph and deep audit planning layer.

    This phase creates the bridge between project memory, multi-AI conversation
    inventory and actual GitHub repositories. It does not mutate repositories.
    It builds a graph and a deterministic audit plan that later write/repair
    phases can execute with explicit approval.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_relationship_graph_status",
            "status": "repo_relationship_graph_ready",
            "graph_file": str(REPO_GRAPH_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized or "repo-project"

    def _load_graph(self) -> Dict[str, Any]:
        if not REPO_GRAPH_FILE.exists():
            return {"repositories": [], "project_links": {}, "audit_plans": []}
        try:
            loaded = json.loads(REPO_GRAPH_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"repositories": [], "project_links": {}, "audit_plans": []}
            loaded.setdefault("repositories", [])
            loaded.setdefault("project_links", {})
            loaded.setdefault("audit_plans", [])
            return loaded
        except json.JSONDecodeError:
            return {"repositories": [], "project_links": {}, "audit_plans": []}

    def _save_graph(self, graph: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        REPO_GRAPH_FILE.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

    def _infer_roles(self, repository_full_name: str, description: str = "", explicit_roles: List[str] | None = None) -> List[str]:
        roles = set(explicit_roles or [])
        text = f"{repository_full_name} {description}".lower()
        for role, hints in ROLE_HINTS.items():
            if any(hint in text for hint in hints):
                roles.add(role)
        return sorted(roles or {"unknown"})

    def _infer_stack(self, roles: List[str], description: str = "") -> List[str]:
        text = description.lower()
        stack = set()
        if "backend" in roles or "fastapi" in text or "python" in text:
            stack.add("python")
            if "fastapi" in text or "backend" in roles:
                stack.add("fastapi")
        if "frontend" in roles or "website" in roles or "next" in text or "react" in text:
            stack.add("typescript")
            if "next" in text or "website" in roles:
                stack.add("nextjs")
        if "mobile" in roles or "android" in text or "apk" in text:
            stack.add("android")
        if "workflow" in roles:
            stack.add("github-actions")
        if "vault" in roles or "supabase" in text:
            stack.add("supabase")
        return sorted(stack)

    def upsert_repository(
        self,
        repository_full_name: str,
        project_id: str | None = None,
        project_name: str | None = None,
        roles: List[str] | None = None,
        description: str = "",
        default_branch: str = "main",
        deploy_targets: List[str] | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        repo_name = repository_full_name.strip()
        if not repo_name:
            return {"ok": False, "error": "repository_full_name_empty"}

        inferred_project_id = project_id or self._slugify(project_name or repo_name.split("/")[-1])
        inferred_project_name = project_name or inferred_project_id.replace("-", " ").title()
        inferred_roles = self._infer_roles(repo_name, description=description, explicit_roles=roles)
        stack = self._infer_stack(inferred_roles, description=description)
        now = self._now()
        repo_id = self._slugify(repo_name)

        graph = self._load_graph()
        existing = None
        for item in graph["repositories"]:
            if item.get("repository_full_name") == repo_name:
                existing = item
                break
        record = existing or {"repo_id": repo_id, "created_at": now}
        record.update(
            {
                "repo_id": repo_id,
                "tenant_id": tenant_id,
                "repository_full_name": repo_name,
                "project_id": inferred_project_id,
                "project_name": inferred_project_name,
                "roles": inferred_roles,
                "stack": stack,
                "description": description,
                "default_branch": default_branch,
                "deploy_targets": sorted(set(deploy_targets or [])),
                "updated_at": now,
            }
        )
        if existing is None:
            graph["repositories"].append(record)

        link = graph["project_links"].setdefault(
            inferred_project_id,
            {
                "project_id": inferred_project_id,
                "project_name": inferred_project_name,
                "repository_ids": [],
                "conversation_ids": [],
                "roles": [],
                "providers": [],
                "updated_at": now,
            },
        )
        link["project_name"] = inferred_project_name
        link["repository_ids"] = sorted(set(link.get("repository_ids", [])) | {repo_id})
        link["roles"] = sorted(set(link.get("roles", [])) | set(inferred_roles))
        link["updated_at"] = now
        self._save_graph(graph)
        return {"ok": True, "mode": "repo_relationship_graph_upsert_repository", "repository": record, "project_link": link}

    def seed_from_conversation_inventory(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        project_map = multi_ai_conversation_inventory_service.build_project_map(tenant_id=tenant_id).get("projects", [])
        graph = self._load_graph()
        now = self._now()
        seeded_projects: List[Dict[str, Any]] = []
        for project in project_map:
            project_id = project.get("project_id", "general-intake")
            link = graph["project_links"].setdefault(
                project_id,
                {
                    "project_id": project_id,
                    "project_name": project.get("project_name", project_id),
                    "repository_ids": [],
                    "conversation_ids": [],
                    "roles": [],
                    "providers": [],
                    "updated_at": now,
                },
            )
            link["project_name"] = project.get("project_name", link.get("project_name", project_id))
            link["conversation_ids"] = sorted(set(link.get("conversation_ids", [])) | set(project.get("conversation_ids", [])))
            link["roles"] = sorted(set(link.get("roles", [])) | set(project.get("repo_roles", [])))
            link["providers"] = sorted(set(link.get("providers", [])) | set(project.get("providers", [])))
            link["updated_at"] = now
            seeded_projects.append(link)
        self._save_graph(graph)
        return {"ok": True, "mode": "repo_relationship_graph_seed_from_conversation_inventory", "project_count": len(seeded_projects), "projects": seeded_projects}

    def build_graph(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        graph = self._load_graph()
        repositories = [item for item in graph.get("repositories", []) if item.get("tenant_id", tenant_id) == tenant_id]
        project_links = list(graph.get("project_links", {}).values())
        repo_by_id = {item["repo_id"]: item for item in repositories}
        projects: List[Dict[str, Any]] = []
        for link in project_links:
            linked_repos = [repo_by_id[repo_id] for repo_id in link.get("repository_ids", []) if repo_id in repo_by_id]
            projects.append({**link, "repositories": linked_repos, "repository_count": len(linked_repos), "conversation_count": len(link.get("conversation_ids", []))})
        projects = sorted(projects, key=lambda item: item.get("updated_at", ""), reverse=True)
        return {
            "ok": True,
            "mode": "repo_relationship_graph",
            "tenant_id": tenant_id,
            "project_count": len(projects),
            "repository_count": len(repositories),
            "projects": projects,
            "repositories": repositories,
        }

    def _audit_steps_for_repository(self, repo: Dict[str, Any]) -> List[Dict[str, Any]]:
        roles = set(repo.get("roles", []))
        steps: List[Dict[str, Any]] = [
            {
                "step_id": "checkout-and-file-inventory",
                "label": "Criar inventário de ficheiros, extensões e estrutura do repo",
                "risk": "safe_read_only",
                "approval_required": False,
            },
            {
                "step_id": "dead-file-and-duplicate-scan",
                "label": "Procurar ficheiros mortos, duplicados e candidatos a limpeza",
                "risk": "safe_read_only",
                "approval_required": False,
            },
            {
                "step_id": "imports-routes-contracts-scan",
                "label": "Validar imports, rotas, contratos API e ligações entre módulos",
                "risk": "safe_read_only",
                "approval_required": False,
            },
            {
                "step_id": "workflow-and-build-scan",
                "label": "Validar GitHub Actions, comandos de build e artefactos esperados",
                "risk": "safe_read_only",
                "approval_required": False,
            },
        ]
        if roles & {"website", "frontend", "studio"}:
            steps.append(
                {
                    "step_id": "frontend-runtime-ui-audit",
                    "label": "Auditar frontend, rotas UI, estados vazios e integração com backend",
                    "risk": "safe_read_only",
                    "approval_required": False,
                }
            )
        if roles & {"backend", "vault"}:
            steps.append(
                {
                    "step_id": "backend-env-vault-audit",
                    "label": "Auditar backend, env vars, secrets esperados e providers de deploy",
                    "risk": "safe_read_only",
                    "approval_required": False,
                }
            )
        steps.append(
            {
                "step_id": "approval-gated-fix-pr-plan",
                "label": "Gerar plano de correção e PRs separadas com aprovação antes de escrita real",
                "risk": "write_requires_approval",
                "approval_required": True,
            }
        )
        return steps

    def build_deep_audit_plan(
        self,
        project_id: str,
        tenant_id: str = "owner-andre",
        include_repair_plan: bool = True,
    ) -> Dict[str, Any]:
        graph_result = self.build_graph(tenant_id=tenant_id)
        project = next((item for item in graph_result.get("projects", []) if item.get("project_id") == project_id), None)
        if project is None:
            return {"ok": False, "error": "project_not_found", "project_id": project_id}

        plan_id = f"audit-{uuid4().hex[:12]}"
        repositories = project.get("repositories", [])
        repo_plans = []
        blockers = []
        if not repositories:
            blockers.append("Projeto ainda não tem repositórios ligados no grafo.")
        if not project.get("conversation_ids"):
            blockers.append("Projeto ainda não tem conversas ligadas no inventário multi-IA.")

        for repo in repositories:
            repo_plans.append(
                {
                    "repo_id": repo.get("repo_id"),
                    "repository_full_name": repo.get("repository_full_name"),
                    "roles": repo.get("roles", []),
                    "stack": repo.get("stack", []),
                    "deploy_targets": repo.get("deploy_targets", []),
                    "steps": self._audit_steps_for_repository(repo),
                }
            )

        plan = {
            "plan_id": plan_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "created_at": self._now(),
            "status": "blocked" if blockers else "ready_for_read_only_audit",
            "include_repair_plan": include_repair_plan,
            "blockers": blockers,
            "conversation_count": project.get("conversation_count", 0),
            "repository_count": len(repositories),
            "repo_plans": repo_plans,
            "global_steps": [
                {
                    "step_id": "merge-ai-context-with-repo-graph",
                    "label": "Cruzar contexto das conversas multi-IA com repos e papéis detetados",
                    "approval_required": False,
                },
                {
                    "step_id": "rank-findings-by-business-impact",
                    "label": "Ordenar falhas por impacto no objetivo do projeto",
                    "approval_required": False,
                },
                {
                    "step_id": "prepare-safe-pr-sequence",
                    "label": "Preparar sequência de PRs pequenas, reversíveis e testáveis",
                    "approval_required": True,
                },
            ],
        }

        graph = self._load_graph()
        graph["audit_plans"].append(plan)
        graph["audit_plans"] = graph["audit_plans"][-200:]
        self._save_graph(graph)
        return {"ok": True, "mode": "repo_relationship_graph_deep_audit_plan", "plan": plan}

    def list_audit_plans(self, tenant_id: str = "owner-andre", project_id: str | None = None, limit: int = 50) -> Dict[str, Any]:
        graph = self._load_graph()
        plans = [item for item in graph.get("audit_plans", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            plans = [item for item in plans if item.get("project_id") == project_id]
        plans = plans[-max(min(limit, 200), 1):]
        return {"ok": True, "mode": "repo_relationship_graph_audit_plan_list", "plan_count": len(plans), "plans": plans}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        graph = self.build_graph(tenant_id=tenant_id)
        plans = self.list_audit_plans(tenant_id=tenant_id, limit=20).get("plans", [])
        missing_repos = [item for item in graph.get("projects", []) if item.get("repository_count", 0) == 0]
        return {
            "ok": True,
            "mode": "repo_relationship_graph_dashboard",
            "tenant_id": tenant_id,
            "project_count": graph.get("project_count", 0),
            "repository_count": graph.get("repository_count", 0),
            "audit_plan_count": len(plans),
            "projects_without_repos": len(missing_repos),
            "projects": graph.get("projects", []),
            "recent_audit_plans": plans,
        }

    def seed_demo_baribudos_graph(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        first = self.upsert_repository(
            repository_full_name="AndreVazao/baribudos-studio",
            project_id="baribudos-studio",
            project_name="Baribudos Studio",
            roles=["studio", "backend", "frontend", "vault"],
            description="Studio cockpit with FastAPI backend, dashboard frontend and Supabase/Vercel configuration.",
            deploy_targets=["vercel", "supabase", "github-actions"],
            tenant_id=tenant_id,
        )
        second = self.upsert_repository(
            repository_full_name="AndreVazao/baribudos-studio-website",
            project_id="baribudos-studio",
            project_name="Baribudos Studio",
            roles=["website", "frontend", "workflow"],
            description="Public website controlled by the Studio cockpit, built with Next.js and GitHub Actions.",
            deploy_targets=["vercel", "github-actions"],
            tenant_id=tenant_id,
        )
        return {"ok": True, "mode": "repo_relationship_graph_seed_demo_baribudos", "repositories": [first.get("repository"), second.get("repository")]}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "repo_relationship_graph_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


repo_relationship_graph_service = RepoRelationshipGraphService()
