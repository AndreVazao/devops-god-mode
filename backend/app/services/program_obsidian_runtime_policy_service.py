from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProgramObsidianRuntimePolicyService:
    """Defines how non-God-Mode programs may use local Obsidian memory."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "program_obsidian_runtime_policy",
            "created_at": _utc_now(),
            "core_rule": "God Mode usa Obsidian para oficina técnica/dev e orquestração. Os outros programas locais usam Obsidian só para trabalho real, operação e evolução de uso.",
            "cloud_exception": "Programas cloud não dependem de Obsidian local; devem usar storage/DB/cloud memory própria.",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Obsidian Runtime Policy",
            "description": "Define quando cada programa pode usar Obsidian local e separa desenvolvimento do God Mode de operação real dos outros programas.",
            "rules": self.rules(),
            "program_classes": self.program_classes(),
            "examples": self.examples(),
        }

    def rules(self) -> list[str]:
        return [
            "Só o God Mode usa Obsidian como oficina técnica de desenvolvimento, prompts, arquitetura e preparação de sync para GitHub.",
            "Programas locais podem usar Obsidian para memória de trabalho real: histórico, notas operacionais, evolução de uso, observações e contexto do utilizador.",
            "Programas locais não devem usar Obsidian como substituto de base de dados aplicacional quando precisam de consistência transacional.",
            "Programas cloud não devem depender de Obsidian local para funcionar; devem usar DB/storage/cloud memory própria.",
            "Quando um programa local encontra bug/feature técnica, o God Mode decide se promove a informação para GitHub memory.",
            "Obsidian local pode alimentar o God Mode, mas não deve virar fonte técnica oficial de código para todos os programas sem curadoria.",
            "Se um programa precisar de memória offline, deve guardar dados críticos na sua própria pasta/DB e apenas espelhar notas humanas no Obsidian.",
        ]

    def program_classes(self) -> dict[str, Any]:
        return {
            "god_mode": {
                "may_use_obsidian_for_development": True,
                "may_use_obsidian_for_runtime": True,
                "purpose": [
                    "orquestração",
                    "oficina técnica local",
                    "prompts",
                    "planeamento",
                    "evolução",
                    "preparação de sync GitHub memory",
                    "contexto operacional local",
                ],
            },
            "local_desktop_or_mobile_programs": {
                "may_use_obsidian_for_development": False,
                "may_use_obsidian_for_runtime": True,
                "purpose": [
                    "histórico de uso real",
                    "notas operacionais",
                    "observações locais",
                    "evolução de comportamento",
                    "relatórios legíveis por humanos",
                ],
                "must_keep_own_data_store_for": [
                    "dados críticos",
                    "estado transacional",
                    "licenças",
                    "pagamentos",
                    "configuração obrigatória",
                    "dados que não podem perder consistência",
                ],
            },
            "cloud_programs": {
                "may_use_obsidian_for_development": False,
                "may_use_obsidian_for_runtime": False,
                "purpose": [
                    "não depender de Obsidian local",
                    "usar DB/storage/cloud memory própria",
                    "opcionalmente exportar resumo para Obsidian via God Mode quando o operador quiser",
                ],
            },
        }

    def classify_program_use(
        self,
        program_name: str,
        is_cloud: bool = False,
        is_god_mode: bool = False,
        requested_use: str | None = None,
    ) -> dict[str, Any]:
        requested = (requested_use or "runtime").strip().lower()
        if is_god_mode or program_name.strip().lower().replace(" ", "_") in {"god_mode", "godmode"}:
            classification = "god_mode"
            allowed = True
        elif is_cloud:
            classification = "cloud_program"
            allowed = False
        else:
            classification = "local_program"
            allowed = requested in {"runtime", "operation", "operational", "evolution", "evolucao", "evolução", "real_work"}
        return {
            "ok": True,
            "program_name": program_name,
            "classification": classification,
            "requested_use": requested,
            "obsidian_allowed": allowed,
            "recommendation": self._recommendation(classification, allowed),
        }

    def _recommendation(self, classification: str, allowed: bool) -> str:
        if classification == "god_mode":
            return "Pode usar Obsidian como oficina técnica/dev e como memória operacional local."
        if classification == "cloud_program":
            return "Não depender de Obsidian local; usar DB/storage/cloud memory própria. Exportar resumo via God Mode apenas se necessário."
        if allowed:
            return "Pode usar Obsidian local para trabalho real/operacional/evolução de uso, mantendo dados críticos na DB própria."
        return "Não usar Obsidian como ambiente de desenvolvimento direto deste programa; passar pelo God Mode."

    def examples(self) -> dict[str, Any]:
        return {
            "proventil_local": {
                "obsidian_use": "notas de obras, observações técnicas locais, evolução operacional",
                "own_store": "clientes, orçamentos, pagamentos, moradas, histórico crítico",
            },
            "verbaforge_local": {
                "obsidian_use": "ideias de séries, observações de produção, decisões criativas locais",
                "own_store": "projetos, publicações, contas, métricas, assets",
            },
            "bot_lords_mobile_local": {
                "obsidian_use": "notas de estratégia, observações de comportamento, evolução de rotina",
                "own_store": "contas, licenças, configurações, jobs, logs críticos",
            },
            "build_control_center_cloud": {
                "obsidian_use": "não obrigatório; apenas resumos exportados pelo God Mode",
                "own_store": "GitHub/Vercel/DB/cloud storage",
            },
        }

    def handoff_note(self) -> dict[str, Any]:
        note = """# Política Obsidian por Programa

## Regra principal

- God Mode pode usar Obsidian como oficina técnica/dev e memória operacional.
- Outros programas locais usam Obsidian apenas para trabalho real, operação e evolução de uso.
- Programas cloud não dependem de Obsidian local.

## Regra prática

Quando um programa local gerar notas relevantes para desenvolvimento, o God Mode recolhe, filtra e decide se promove para GitHub memory.

Quando um programa cloud precisar de memória persistente, usa DB/storage/cloud memory própria.
""".strip()
        return {"ok": True, "note": note}

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "program_classes": self.program_classes(),
            "examples": self.examples(),
            "handoff_note": self.handoff_note(),
        }


program_obsidian_runtime_policy_service = ProgramObsidianRuntimePolicyService()
