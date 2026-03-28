from typing import Any


class RepoTreeAnalysisV2:
    def analyze(self, tree_json: dict[str, Any]) -> dict[str, Any]:
        names: list[str] = []
        self._collect_names(tree_json, names)
        lower_names = {name.lower() for name in names}

        frameworks: list[str] = []
        repo_types: list[str] = []
        recommendations: list[str] = []
        risks: list[dict[str, str]] = []
        contract_hints: list[str] = []

        if "package.json" in lower_names:
            frameworks.append("node")
        if "requirements.txt" in lower_names:
            frameworks.append("python")
        if any(name.endswith("next.config.js") or name.endswith("next.config.mjs") for name in lower_names):
            frameworks.append("nextjs")
        if any(name.endswith("schema.prisma") for name in lower_names):
            frameworks.append("prisma")
        if any("api" == name or name.endswith("/api") for name in lower_names):
            frameworks.append("api-surface")
        if "release_manifest.json" in lower_names:
            frameworks.append("release-channel")

        if "client" in lower_names or any(name.startswith("client/") for name in lower_names):
            repo_types.append("client-app")
        if "studio_core" in lower_names or any(name.startswith("studio_core/") for name in lower_names):
            repo_types.append("backend-service")
        if ".github" in lower_names or any(name.startswith(".github/") for name in lower_names):
            repo_types.append("ci-aware")
        if "deploy" in lower_names or any(name.startswith("deploy/") for name in lower_names):
            repo_types.append("deployment-aware")
        if "official_studio_website_contract.txt" in lower_names:
            repo_types.append("contract-aware")
        if any(name.endswith("runbook-pc.md") for name in lower_names):
            repo_types.append("pc-operable")

        if "official_studio_website_contract.txt" in lower_names:
            contract_hints.append("Existe contrato explícito Studio ↔ Website dentro da repo.")
        if any(name.endswith("repository_tree_reference.txt") for name in lower_names):
            contract_hints.append("Repo já mantém ficheiro de referência estrutural; convém sincronizar com o Tree Explorer.")
        if any(name.endswith("readme-deploy.md") for name in lower_names):
            contract_hints.append("Existe documentação de deploy dedicada; usar como fonte de governança operacional.")

        if "version.remote.json" in lower_names:
            recommendations.append("Validar política de versionamento remoto e update channel.")
        if any(name.startswith("deploy/") for name in lower_names):
            recommendations.append("Rever scripts de deploy e separar claramente bootstrap, build e release.")
        if "studio_core" in lower_names:
            recommendations.append("Alinhar contrato entre studio_core, client e website público através do registry.")
        if "official_studio_website_contract.txt" in lower_names:
            recommendations.append("Ler e validar o contrato oficial Studio-Website contra o registry persistido do God Mode.")
        if any(name.endswith("repository_tree_reference.txt") for name in lower_names):
            recommendations.append("Comparar árvore real com REPOSITORY_TREE_REFERENCE.txt para detetar drift estrutural.")

        if ".env.example" in lower_names:
            risks.append({
                "key": "env_template_present",
                "severity": "low",
                "message": "Template de variáveis encontrado; validar se não existem segredos reais próximos.",
            })
        if any(name.endswith("version.remote.json") for name in lower_names):
            risks.append({
                "key": "remote_versioning_surface",
                "severity": "medium",
                "message": "Repo expõe superfície de versionamento remoto; validar governança de release.",
            })
        if any(name.startswith("deploy/") for name in lower_names) and any(name.startswith("client/") for name in lower_names):
            risks.append({
                "key": "mixed_delivery_surface",
                "severity": "medium",
                "message": "Repo mistura cliente e superfície de deploy; convém vigiar fronteiras arquiteturais.",
            })
        if "official_studio_website_contract.txt" in lower_names and "repository_tree_reference.txt" in lower_names:
            risks.append({
                "key": "contract_tree_drift_risk",
                "severity": "medium",
                "message": "Há contrato oficial e ficheiro de árvore de referência; convém verificar drift entre documentação e estrutura real.",
            })

        score = 50
        score += 10 if "python" in frameworks else 0
        score += 10 if "node" in frameworks else 0
        score += 10 if "ci-aware" in repo_types else 0
        score += 10 if "deployment-aware" in repo_types else 0
        score += 5 if "contract-aware" in repo_types else 0
        score += 5 if "pc-operable" in repo_types else 0
        score -= 10 if any(risk["severity"] == "medium" for risk in risks) else 0
        score = max(0, min(100, score))

        return {
            "frameworks": sorted(set(frameworks)),
            "repo_types": sorted(set(repo_types)),
            "contract_hints": contract_hints,
            "risks": risks,
            "recommendations": recommendations,
            "structural_score": score,
            "next_action": recommendations[0] if recommendations else "Continuar análise progressiva.",
        }

    def _collect_names(self, node: dict[str, Any], items: list[str], parent_path: str = "") -> None:
        name = node.get("name", "")
        current_path = name if not parent_path else f"{parent_path}/{name}"
        if name:
            items.append(name)
            items.append(current_path)
        for child in node.get("children", []):
            self._collect_names(child, items, current_path if name else parent_path)


repo_tree_analysis_v2 = RepoTreeAnalysisV2()
