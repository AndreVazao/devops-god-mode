from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings
from app.services.github_service import github_service


@dataclass
class InferredRepo:
    full_name: str
    repo_name: str
    visibility: str | None
    default_branch: str | None
    html_url: str | None
    language: str | None
    role: str | None
    runtime: str | None
    stack_json: dict[str, Any]
    common_files_json: dict[str, Any]
    recent_commits_json: list[dict[str, Any]]
    summary_json: dict[str, Any]


class RegistryService:
    def __init__(self) -> None:
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY

    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def _headers(self) -> dict[str, str]:
        if not self.is_configured():
            raise RuntimeError("supabase_not_configured")
        return {
            "apikey": str(settings.SUPABASE_KEY),
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }

    def _infer_role_and_runtime(self, repo: dict[str, Any]) -> tuple[str | None, str | None]:
        full_name = repo.get("full_name") or ""
        frameworks = ((repo.get("stack") or {}).get("frameworks") or [])
        runtimes = ((repo.get("stack") or {}).get("runtimes") or [])

        if full_name.endswith("baribudos-studio"):
            return "private_production_brain", "private_local_or_family_control_plane"
        if full_name.endswith("baribudos-studio-website"):
            return "public_commerce_runtime", "public_cloud"
        if full_name.endswith("devops-god-mode"):
            return "meta_devops_orchestrator", "cloud_backend_mobile_first_panel"
        if full_name.endswith("ai-devops-control-center"):
            return "devops_control_ui_or_service", "node_service_or_dashboard"
        if "nextjs" in frameworks:
            return "public_web_app", "public_cloud"
        if "fastapi" in frameworks:
            return "backend_service", "cloud_or_private_backend"
        if "node" in runtimes and "python" in runtimes:
            return "hybrid_service", "mixed_runtime"
        if "node" in runtimes:
            return "node_service", "cloud_or_server_runtime"
        if "python" in runtimes:
            return "python_service", "cloud_or_server_runtime"
        return None, None

    def _infer_ecosystems(self, repositories: list[dict[str, Any]]) -> dict[str, Any]:
        ecosystems: list[dict[str, Any]] = []
        relations: list[dict[str, str]] = []
        risks: list[dict[str, Any]] = []
        unclassified: list[dict[str, Any]] = []
        ecosystem_repo_names: set[str] = set()

        full_names = {repo.get("full_name") for repo in repositories}

        if {
            "AndreVazao/baribudos-studio",
            "AndreVazao/baribudos-studio-website",
        }.issubset(full_names):
            ecosystems.append(
                {
                    "key": "baribudos-ecosystem",
                    "display_name": "Baribudos Ecosystem",
                    "type": "single_product_view",
                    "description": "Studio privado de produção ligado ao website público comercial.",
                    "repos": [
                        "AndreVazao/baribudos-studio",
                        "AndreVazao/baribudos-studio-website",
                    ],
                }
            )
            ecosystem_repo_names.update(
                [
                    "AndreVazao/baribudos-studio",
                    "AndreVazao/baribudos-studio-website",
                ]
            )
            relations.extend(
                [
                    {
                        "source": "AndreVazao/baribudos-studio",
                        "target": "AndreVazao/baribudos-studio-website",
                        "relation_type": "publishes_to",
                    },
                    {
                        "source": "AndreVazao/baribudos-studio-website",
                        "target": "AndreVazao/baribudos-studio",
                        "relation_type": "consumes_catalog_from",
                    },
                ]
            )

        if {
            "AndreVazao/devops-god-mode",
            "AndreVazao/ai-devops-control-center",
        }.issubset(full_names):
            ecosystems.append(
                {
                    "key": "devops-meta-ecosystem",
                    "display_name": "DevOps Meta Ecosystem",
                    "type": "meta_governance_system",
                    "description": "Camada meta de controlo DevOps e superfícies relacionadas.",
                    "repos": [
                        "AndreVazao/devops-god-mode",
                        "AndreVazao/ai-devops-control-center",
                    ],
                }
            )
            ecosystem_repo_names.update(
                [
                    "AndreVazao/devops-god-mode",
                    "AndreVazao/ai-devops-control-center",
                ]
            )
            relations.append(
                {
                    "source": "AndreVazao/devops-god-mode",
                    "target": "AndreVazao/ai-devops-control-center",
                    "relation_type": "related_devops_surface",
                }
            )

        for repo in repositories:
            full_name = repo.get("full_name") or ""
            if full_name not in ecosystem_repo_names:
                unclassified.append(
                    {
                        "full_name": full_name,
                        "reason": "not_mapped_yet",
                    }
                )

            if full_name == "AndreVazao/baribudos-studio-website":
                recent_messages = [item.get("message", "") for item in (repo.get("recent_commits") or [])]
                if any("env.production" in message for message in recent_messages):
                    risks.append(
                        {
                            "repo_full_name": full_name,
                            "flag_key": "website_recent_env_file_history",
                            "severity": "high",
                            "title": "Histórico recente de env em repo público/comercial",
                            "description": "Foram detetados commits recentes com env.production no histórico do website.",
                        }
                    )
                    risks.append(
                        {
                            "repo_full_name": full_name,
                            "flag_key": "studio_website_contract_alignment_required",
                            "severity": "medium",
                            "title": "Contrato Studio-Website precisa de alinhamento",
                            "description": "O ecossistema Baribudos precisa de ponte contratual entre produção privada e runtime comercial.",
                        }
                    )

        return {
            "ecosystems": ecosystems,
            "relations": relations,
            "risks": risks,
            "unclassified_repos": unclassified,
        }

    async def build_preview(self, limit: int = 10) -> dict[str, Any]:
        if not github_service.is_configured():
            raise RuntimeError("github_not_configured")

        scan_result = await github_service.scan_repositories(limit=limit)
        inferred = self._infer_ecosystems(scan_result.get("repositories") or [])

        enriched_repos: list[dict[str, Any]] = []
        for repo in scan_result.get("repositories") or []:
            role, runtime = self._infer_role_and_runtime(repo)
            enriched_repos.append(
                {
                    **repo,
                    "inferred_role": role,
                    "inferred_runtime": runtime,
                }
            )

        return {
            "ok": True,
            "mode": "preview",
            "limit": limit,
            "scan": {
                "count": scan_result.get("count", 0),
                "success_count": scan_result.get("success_count", 0),
                "error_count": scan_result.get("error_count", 0),
                "partial": scan_result.get("partial", False),
            },
            "ecosystems": inferred.get("ecosystems", []),
            "relations": inferred.get("relations", []),
            "risks": inferred.get("risks", []),
            "unclassified_repos": inferred.get("unclassified_repos", []),
            "repositories": enriched_repos,
            "approval_required": True,
            "next_action": "Se estiver correto, usar POST /registry/github-ingest?limit=<n> para gravar na base de dados.",
        }

    async def _supabase_post(self, path: str, payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/{path}",
                headers=self._headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json() if response.text else []

    async def _supabase_get(self, path: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/{path}",
                headers={
                    "apikey": str(settings.SUPABASE_KEY),
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json() if response.text else []

    async def ingest_preview(self, limit: int = 10) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("supabase_not_configured")

        preview = await self.build_preview(limit=limit)
        ecosystems = preview.get("ecosystems", [])
        repositories = preview.get("repositories", [])
        relations = preview.get("relations", [])
        risks = preview.get("risks", [])

        ecosystem_rows = [
            {
                "key": item["key"],
                "display_name": item["display_name"],
                "type": item["type"],
                "description": item.get("description"),
            }
            for item in ecosystems
        ]
        if ecosystem_rows:
            await self._supabase_post("ecosystems?on_conflict=key", ecosystem_rows)

        ecosystem_lookup_rows = await self._supabase_get("ecosystems?select=id,key")
        ecosystem_map = {item["key"]: item["id"] for item in ecosystem_lookup_rows}

        repo_ecosystem_map: dict[str, str] = {}
        for ecosystem in ecosystems:
            ecosystem_id = ecosystem_map.get(ecosystem["key"])
            if not ecosystem_id:
                continue
            for full_name in ecosystem.get("repos", []):
                repo_ecosystem_map[full_name] = ecosystem_id

        repo_rows = []
        for repo in repositories:
            repo_rows.append(
                {
                    "ecosystem_id": repo_ecosystem_map.get(repo.get("full_name")),
                    "full_name": repo.get("full_name"),
                    "repo_name": repo.get("name"),
                    "visibility": repo.get("visibility"),
                    "default_branch": repo.get("default_branch"),
                    "html_url": repo.get("html_url"),
                    "language": repo.get("language"),
                    "role": repo.get("inferred_role"),
                    "runtime": repo.get("inferred_runtime"),
                    "status": "scanned",
                    "stack_json": repo.get("stack") or {},
                    "common_files_json": repo.get("common_files") or {},
                    "recent_commits_json": repo.get("recent_commits") or [],
                    "summary_json": repo.get("summary") or {},
                    "last_scan_at": "now()",
                }
            )
        if repo_rows:
            await self._supabase_post("repos?on_conflict=full_name", repo_rows)

        repo_lookup_rows = await self._supabase_get("repos?select=id,full_name")
        repo_map = {item["full_name"]: item["id"] for item in repo_lookup_rows}

        relation_rows = []
        for relation in relations:
            source_repo_id = repo_map.get(relation["source"])
            target_repo_id = repo_map.get(relation["target"])
            if source_repo_id and target_repo_id:
                relation_rows.append(
                    {
                        "source_repo_id": source_repo_id,
                        "target_repo_id": target_repo_id,
                        "relation_type": relation["relation_type"],
                    }
                )
        if relation_rows:
            await self._supabase_post(
                "repo_relations?on_conflict=source_repo_id,target_repo_id,relation_type",
                relation_rows,
            )

        risk_rows = []
        for risk in risks:
            repo_id = repo_map.get(risk["repo_full_name"])
            if repo_id:
                risk_rows.append(
                    {
                        "repo_id": repo_id,
                        "flag_key": risk["flag_key"],
                        "severity": risk["severity"],
                        "status": "open",
                        "title": risk["title"],
                        "description": risk["description"],
                    }
                )
        if risk_rows:
            await self._supabase_post("risk_flags", risk_rows)

        return {
            "ok": True,
            "mode": "ingest",
            "ecosystems_written": len(ecosystem_rows),
            "repos_written": len(repo_rows),
            "relations_written": len(relation_rows),
            "risks_written": len(risk_rows),
            "message": "Preview confirmada e registry gravado na Supabase.",
        }


registry_service = RegistryService()
