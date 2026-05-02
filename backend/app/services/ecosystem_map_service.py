from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


ECOSYSTEM_DOC_PATH = "docs/arquitetura/ECOSSISTEMA_ANDREVAZAO_GRUPOS_E_ARQUIVO.md"
ECOSYSTEM_OPERATIONAL_DOC_PATH = "docs/arquitetura/ECOSSISTEMA_ANDREVAZAO_OPERACIONAL.md"

GROUPS: dict[str, dict[str, Any]] = {
    "01_GOD_MODE_E_SUBSISTEMAS": {
        "name": "God Mode e subsistemas",
        "keywords": ["god mode", "devops", "build", "github", "organizer", "andreos", "memory", "vortexa", "automation", "agent", "orchestrator"],
        "execution_default": "HIBRIDO",
        "license_default": "interno_apenas",
    },
    "02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO": {
        "name": "Baribudos Studio e criadores de conteúdo",
        "keywords": ["baribudos", "verbaforge", "viral", "content", "conteudo", "ebook", "video", "tts", "voice", "lipsync", "translation", "curso"],
        "execution_default": "HIBRIDO",
        "license_default": "por_modulo",
    },
    "03_MECANICA_ECUPROTUNE_SWAPAI_OUTROS": {
        "name": "Mecânica, ECUProTune, SwapAI e outros",
        "keywords": ["ecu", "obd", "elm327", "swap", "motor", "mecanica", "diagnostico", "reprogramacao", "konnwei", "performance"],
        "execution_default": "LOCAL",
        "license_default": "profissional",
    },
    "04_DESENHO_E_CONVERSOR_CNC": {
        "name": "Desenho e conversor CNC",
        "keywords": ["gcode", "dxf", "cnc", "laser", "svg", "stl", "step", "cad", "desenho", "conversor", "opencv"],
        "execution_default": "LOCAL",
        "license_default": "profissional",
    },
    "05_PROVENTIL_VIDEO_PORTEIRO_EXTRATORES_FUMOS": {
        "name": "ProVentil, videoporteiro e extratores de fumos",
        "keywords": ["proventil", "videoporteiro", "porteiro", "comelit", "fermax", "bticino", "fumos", "extrator", "botoneira", "climastore", "orcamento"],
        "execution_default": "HIBRIDO",
        "license_default": "interno_apenas",
    },
    "06_BOT_FACTORY_ENGENHARIA_REVERSA_PCFARM_BOTS_JOGO": {
        "name": "Bot Factory, engenharia reversa, PCFarm e bots de jogo",
        "keywords": ["bot factory", "reverse", "engenharia reversa", "lords", "pcfarm", "jogo", "game", "rally", "darknest", "ocr", "headless", "emulator"],
        "execution_default": "LOCAL",
        "license_default": "por_conta",
    },
    "07_BOTS_PROGRAMAS_E_EXCHANGE": {
        "name": "Bots programas e exchange",
        "keywords": ["exchange", "trading", "bot programa", "marketplace", "scraping", "portfolio", "alerta", "automacao", "financeiro"],
        "execution_default": "HIBRIDO",
        "license_default": "por_modulo",
    },
    "08_MOBILE": {
        "name": "Mobile",
        "keywords": ["mobile", "android", "apk", "overlay", "adb", "expo", "kotlin", "telemovel", "phone", "andreos"],
        "execution_default": "MOBILE",
        "license_default": "por_utilizador",
    },
    "09_ONER_CORE_E_CHAT_BOTS": {
        "name": "Oner Core e chat bots",
        "keywords": ["oner", "licenca", "pagamento", "admin", "chatbot", "permissao", "comissao", "bonus", "auth", "utilizador"],
        "execution_default": "CLOUD",
        "license_default": "cloud_saas",
    },
    "10_SHEETPRO_E_PROGRAMAS_PESSOAIS": {
        "name": "SheetPro e programas pessoais",
        "keywords": ["sheetpro", "escala", "chapa", "pdf", "rota", "servico", "horario", "pessoal", "utilitario"],
        "execution_default": "LOCAL",
        "license_default": "interno_apenas",
    },
    "11_REUSABLE_CODES": {
        "name": "Reusable Codes",
        "keywords": ["reusable", "codigo reutilizavel", "component", "pattern", "script", "helper", "template", "meta", "biblioteca"],
        "execution_default": "ARQUIVO",
        "license_default": "interno_apenas",
    },
    "12_ETC_INCUBADORA_FUTURA": {
        "name": "ETC / Incubadora futura",
        "keywords": ["ideia", "incubadora", "poc", "prova conceito", "teste rapido", "futuro", "sem grupo"],
        "execution_default": "ARQUIVO",
        "license_default": "a_definir",
    },
}

KNOWN_REPOS: dict[str, str] = {
    "AndreVazao/devops-god-mode": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/ai-devops-control-center": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/universal-build-platform": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/build-control-center": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/build-control-panel": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/GitHub-auto-builder": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/Project-Organizer-AI": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/ENV-editor": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/Vortexa-core": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/andreos-memory": "01_GOD_MODE_E_SUBSISTEMAS",
    "AndreVazao/baribudos-studio": "02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO",
    "AndreVazao/baribudos-studio-primary": "02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO",
    "AndreVazao/baribudos-studio-home-edition": "02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO",
    "AndreVazao/baribudos-studio-website": "02_BARIBUDOS_STUDIO_E_CRIADORES_CONTEUDO",
    "AndreVazao/ecu-pro-tune": "03_MECANICA_ECUPROTUNE_SWAPAI_OUTROS",
    "AndreVazao/proventil": "05_PROVENTIL_VIDEO_PORTEIRO_EXTRATORES_FUMOS",
    "AndreVazao/Bot_Factory": "06_BOT_FACTORY_ENGENHARIA_REVERSA_PCFARM_BOTS_JOGO",
    "AndreVazao/script-reviewer-mobile": "08_MOBILE",
    "AndreVazao/SheetProPrivate": "10_SHEETPRO_E_PROGRAMAS_PESSOAIS",
}

EXECUTION_TYPES = ["LOCAL", "CLOUD", "HIBRIDO", "MOBILE", "ARQUIVO"]
LICENSE_TYPES = [
    "interno_apenas",
    "gratuito",
    "pessoal",
    "profissional",
    "por_cliente",
    "por_conta",
    "por_castelo",
    "por_modulo",
    "por_utilizador",
    "por_obra",
    "cloud_saas",
    "a_definir",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EcosystemMapService:
    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "ecosystem_map",
            "created_at": _utc_now(),
            "source_doc": ECOSYSTEM_DOC_PATH,
            "operational_doc": ECOSYSTEM_OPERATIONAL_DOC_PATH,
            "group_count": len(GROUPS),
            "known_repo_count": len(KNOWN_REPOS),
            "execution_types": EXECUTION_TYPES,
            "license_types": LICENSE_TYPES,
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Ecossistema AndreVazao — mapa operacional",
            "description": "Classifica projetos/repos por grupo, tipo de execução, licenciamento e destino de arquivo/reusable codes.",
            "primary_actions": [
                {"label": "Classificar projeto", "endpoint": "/api/ecosystem-map/classify", "method": "POST", "safe": True},
                {"label": "Ver grupos", "endpoint": "/api/ecosystem-map/groups", "method": "GET", "safe": True},
                {"label": "Repos conhecidos", "endpoint": "/api/ecosystem-map/repos", "method": "GET", "safe": True},
                {"label": "Decidir Reusable Code", "endpoint": "/api/ecosystem-map/reusable-decision", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "God Mode é o orquestrador central, não um monorepo obrigatório de todos os projetos.",
            "Todo projeto deve ter grupo oficial, tipo de execução e licenciamento provável.",
            "Projetos novos sem grupo vão para 12_ETC_INCUBADORA_FUTURA até maturarem.",
            "Projetos antigos não são apagados antes de análise e extração de Reusable Codes.",
            "Código reutilizável deve ter metadata e entrar no Reusable Code Registry.",
            "GitHub memory guarda estado técnico estável; Obsidian local guarda evolução operacional/local.",
            "Programas cloud não dependem de Obsidian local.",
        ]

    def groups(self) -> dict[str, Any]:
        return {"ok": True, "groups": GROUPS}

    def repos(self) -> dict[str, Any]:
        return {"ok": True, "known_repos": KNOWN_REPOS}

    def classify(
        self,
        name: str,
        description: str | None = None,
        repo: str | None = None,
        is_cloud: bool | None = None,
        is_mobile: bool | None = None,
    ) -> dict[str, Any]:
        if repo and repo in KNOWN_REPOS:
            group_id = KNOWN_REPOS[repo]
            match_reason = "known_repo_map"
            score = 999
        else:
            group_id, score, match_reason = self._keyword_classify(name=name, description=description)
        group = GROUPS[group_id]
        execution_type = self._execution_type(group, name, description, is_cloud, is_mobile)
        license_type = self._license_type(group, name, description, execution_type)
        memory_policy = self._memory_policy(execution_type, group_id)
        return {
            "ok": True,
            "name": name,
            "repo": repo,
            "group_id": group_id,
            "group_name": group["name"],
            "score": score,
            "match_reason": match_reason,
            "execution_type": execution_type,
            "license_type": license_type,
            "memory_policy": memory_policy,
            "recommended_next_actions": self._next_actions(group_id, execution_type, repo),
        }

    def _keyword_classify(self, name: str, description: str | None) -> tuple[str, int, str]:
        text = f"{name}\n{description or ''}".lower()
        best_group = "12_ETC_INCUBADORA_FUTURA"
        best_score = 0
        for group_id, group in GROUPS.items():
            score = 0
            for keyword in group["keywords"]:
                if keyword.lower() in text:
                    score += 10 + len(keyword.split())
            if score > best_score:
                best_score = score
                best_group = group_id
        if best_score == 0:
            return "12_ETC_INCUBADORA_FUTURA", 0, "no_keyword_match_incubator_default"
        return best_group, best_score, "keyword_match"

    def _execution_type(
        self,
        group: dict[str, Any],
        name: str,
        description: str | None,
        is_cloud: bool | None,
        is_mobile: bool | None,
    ) -> str:
        if is_cloud is True:
            return "CLOUD"
        if is_mobile is True:
            return "MOBILE"
        text = f"{name}\n{description or ''}".lower()
        if any(token in text for token in ["apk", "android", "mobile", "telemovel", "overlay"]):
            return "MOBILE"
        if any(token in text for token in ["cloud", "saas", "vercel", "online", "server", "web dashboard"]):
            return "CLOUD"
        if any(token in text for token in ["desktop", "pc", "local", "exe", "sqlite", "ollama", "obsidian"]):
            return "LOCAL"
        return group["execution_default"]

    def _license_type(self, group: dict[str, Any], name: str, description: str | None, execution_type: str) -> str:
        text = f"{name}\n{description or ''}".lower()
        if "castelo" in text or "castle" in text:
            return "por_castelo"
        if "conta" in text or "account" in text:
            return "por_conta"
        if "obra" in text or "cliente" in text:
            return "por_cliente"
        if execution_type == "CLOUD":
            return "cloud_saas"
        return group["license_default"]

    def _memory_policy(self, execution_type: str, group_id: str) -> dict[str, Any]:
        if group_id == "01_GOD_MODE_E_SUBSISTEMAS":
            return {
                "github_memory": "technical_source_of_truth",
                "obsidian": "development_workshop_and_local_operations",
                "cloud_memory": "optional_for_cloud_modules",
            }
        if execution_type == "CLOUD":
            return {
                "github_memory": "technical_source_of_truth",
                "obsidian": "optional_exported_summary_only",
                "cloud_memory": "required_for_runtime",
            }
        if execution_type in {"LOCAL", "MOBILE", "HIBRIDO"}:
            return {
                "github_memory": "technical_source_of_truth_when_stable",
                "obsidian": "runtime_operations_and_usage_evolution",
                "local_store": "required_for_critical_data",
            }
        return {
            "github_memory": "archive_metadata_if_useful",
            "obsidian": "notes_until_decision",
            "reusable_registry": "extract_useful_parts_before_deletion",
        }

    def _next_actions(self, group_id: str, execution_type: str, repo: str | None) -> list[str]:
        actions = [
            "verificar reusable-code-registry antes de gerar código novo",
            "criar/atualizar memória técnica GitHub se virar decisão estável",
        ]
        if not repo:
            actions.append("verificar se já existe repo antes de criar novo")
        if group_id == "12_ETC_INCUBADORA_FUTURA":
            actions.append("manter em incubadora até maturar grupo definitivo")
        if execution_type == "CLOUD":
            actions.append("garantir DB/storage/cloud memory própria")
        if execution_type in {"LOCAL", "MOBILE"}:
            actions.append("usar Obsidian apenas para operação/evolução, exceto God Mode")
        return actions

    def reusable_decision(
        self,
        purpose: str,
        source_project: str | None = None,
        source_repo: str | None = None,
        files: list[str] | None = None,
    ) -> dict[str, Any]:
        text = f"{purpose}\n{source_project or ''}\n{source_repo or ''}\n{' '.join(files or [])}".lower()
        reusable_markers = [
            "script",
            "helper",
            "pattern",
            "template",
            "workflow",
            "api",
            "service",
            "route",
            "component",
            "dashboard",
            "installer",
            "converter",
            "ocr",
            "adb",
            "gcode",
            "dxf",
            "auth",
            "license",
        ]
        hits = [marker for marker in reusable_markers if marker in text]
        should_register = bool(hits) or len(files or []) > 0
        return {
            "ok": True,
            "purpose": purpose,
            "source_project": source_project,
            "source_repo": source_repo,
            "files": files or [],
            "should_register_reusable_code": should_register,
            "hits": hits,
            "target_group": "11_REUSABLE_CODES" if should_register else "12_ETC_INCUBADORA_FUTURA",
            "metadata_required": should_register,
            "next_action": "register_in_reusable_code_registry" if should_register else "keep_in_obsidian_or_incubator_until_clear",
        }

    def archive_decision(
        self,
        project_name: str,
        has_repo: bool = True,
        has_reusable_code: bool = False,
        is_replaced: bool = False,
        is_validated: bool = False,
    ) -> dict[str, Any]:
        if has_reusable_code:
            status = "REUTILIZAVEL"
        elif is_replaced:
            status = "SUBSTITUIDO"
        elif is_validated:
            status = "ARQUIVADO_UTIL"
        else:
            status = "NAO_VALIDADO"
        return {
            "ok": True,
            "project_name": project_name,
            "archive_status": status,
            "can_delete": False,
            "required_before_delete": [
                "analisar scripts/configs/prompts/db/ui",
                "extrair reusable codes",
                "guardar metadata",
                "registar decisão em GitHub memory",
                "confirmar explicitamente com Oner",
            ],
            "recommendation": "não apagar automaticamente; arquivar/congelar depois de extrair valor",
        }

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "groups": self.groups(),
            "repos": self.repos(),
            "rules": self.rules(),
        }


ecosystem_map_service = EcosystemMapService()
