from __future__ import annotations

from typing import Any

from app.services.github_service import github_service


class RegistryService:
    def __init__(self) -> None:
        self.runtime_mode = "local_first_pc_phone"

    def is_configured(self) -> bool:
        return github_service.is_configured()

    def local_mode_summary(self) -> dict[str, Any]:
        return {
            "runtime_mode": self.runtime_mode,
            "storage_mode": "local_preview_only",
            "cloud_legacy_removed": True,
            "ingest_mode": "disabled",
            "source_of_truth": "pc_and_phone_runtime",
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
            return "meta_devops_orchestrator", "pc_brain_mobile_cockpit"
        if full_name.endswith("ai-devops-control-center"):
            return "devops_control_ui_or_service", "local_dashboard_or_bridge"
        if "nextjs" in frameworks:
            return "public_web_app", "public_cloud"
        if "fastapi" in frameworks and full_name.endswith("devops-god-mode"):
            return "backend_service", "pc_local_backend"
        if "fastapi" in frameworks:
            return "backend_service", "private_backend"
        if "node" in runtimes and "python" in runtimes:
            return "hybrid_service", "mixed_runtime"
        if "node" in runtimes:
            return "node_service", "server_or_local_runtime"
        if "python" in runtimes:
            return "python_service", "server_or_local_runtime"
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
            "registry_runtime": self.local_mode_summary(),
            "ecosystems": inferred.get("ecosystems", []),
            "relations": inferred.get("relations", []),
            "risks": inferred.get("risks", []),
            "unclassified_repos": inferred.get("unclassified_repos", []),
            "repositories": enriched_repos,
            "approval_required": False,
            "next_action": "Usar este preview como mapa local da stack e continuar a consolidação PC + telefone.",
        }

    async def ingest_preview(self, limit: int = 10) -> dict[str, Any]:
        preview = await self.build_preview(limit=limit)
        return {
            "ok": False,
            "mode": "ingest_disabled",
            "limit": limit,
            "registry_runtime": self.local_mode_summary(),
            "message": "O ingest cloud foi desativado. O registry agora funciona só em preview local-first.",
            "preview_summary": preview.get("scan", {}),
            "repositories": preview.get("repositories", []),
            "ecosystems": preview.get("ecosystems", []),
            "relations": preview.get("relations", []),
            "risks": preview.get("risks", []),
            "unclassified_repos": preview.get("unclassified_repos", []),
        }


registry_service = RegistryService()
