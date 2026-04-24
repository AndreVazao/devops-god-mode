from __future__ import annotations

from typing import Any, Dict, List

from app.services.godmode_diagnostics_service import godmode_diagnostics_service
from app.services.operator_action_journal_service import operator_action_journal_service
from app.services.operator_pending_attention_service import operator_pending_attention_service
from app.services.secret_vault_service import secret_vault_service


class GodModeRemediationService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "godmode_remediation_status",
            "status": "godmode_remediation_ready",
        }

    def build_plan(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        diagnostics = godmode_diagnostics_service.build_dashboard(tenant_id=tenant_id)
        attention = operator_pending_attention_service.build_attention_feed(tenant_id=tenant_id)
        secrets = secret_vault_service.list_secrets()
        journal = operator_action_journal_service.list_entries(tenant_id=tenant_id, limit=50)

        actions: List[Dict[str, Any]] = []

        if diagnostics.get("provider_count", 0) < 3:
            actions.append(
                {
                    "action_id": "connect-providers",
                    "priority": "critical",
                    "title": "Ligar providers principais",
                    "reason": "Sem providers suficientes, o God Mode não consegue criar e publicar projetos em cadeia.",
                    "target_area": "providers",
                    "expected_gain": "Desbloqueia criação de repo, deploy e persistência para novos projetos.",
                }
            )

        if secrets.get("secret_count", 0) == 0:
            actions.append(
                {
                    "action_id": "seed-vault",
                    "priority": "critical",
                    "title": "Carregar secrets mínimos no vault",
                    "reason": "Sem secrets guardados, os fluxos de deploy e integrações falham cedo.",
                    "target_area": "vault",
                    "expected_gain": "Permite automação real em builds, APIs e ambientes runtime.",
                }
            )

        if attention.get("waiting_thread_count", 0) > 0:
            actions.append(
                {
                    "action_id": "clear-pending-threads",
                    "priority": "high",
                    "title": "Fechar pendências do operador",
                    "reason": "Threads pendentes seguram aprovações, inputs e continuação dos fluxos ativos.",
                    "target_area": "operator_threads",
                    "expected_gain": "Reduz bloqueios manuais e limpa a fila de execução atual.",
                }
            )

        failed_events = [
            item
            for item in journal.get("entries", [])
            if item.get("outcome") in {"failed", "error", "restart_required"}
        ]
        if failed_events:
            actions.append(
                {
                    "action_id": "triage-recent-failures",
                    "priority": "high",
                    "title": "Analisar falhas recentes",
                    "reason": f"Existem {len(failed_events)} eventos recentes com falha, erro ou restart obrigatório.",
                    "target_area": "recovery",
                    "expected_gain": "Ajuda a fechar inconsistências antes de escalar para mais projetos pendurados.",
                }
            )

        if not actions:
            actions.append(
                {
                    "action_id": "expand-project-throughput",
                    "priority": "medium",
                    "title": "Começar a atacar backlog de projetos",
                    "reason": "O cockpit não encontrou bloqueios críticos nesta leitura.",
                    "target_area": "project_backlog",
                    "expected_gain": "Permite usar o God Mode como copiloto real para montar os próximos projetos.",
                }
            )

        actions = sorted(
            actions,
            key=lambda item: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item["priority"], 9),
        )

        return {
            "ok": True,
            "mode": "godmode_remediation_plan",
            "plan_status": "godmode_remediation_plan_ready",
            "tenant_id": tenant_id,
            "action_count": len(actions),
            "actions": actions,
            "diagnostics_summary": {
                "blocker_count": diagnostics.get("blocker_count", 0),
                "provider_count": diagnostics.get("provider_count", 0),
                "secret_count": diagnostics.get("secret_count", 0),
                "pending_threads": attention.get("waiting_thread_count", 0),
                "recent_failures": len(failed_events),
            },
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "godmode_remediation_package",
            "package": {
                "status": self.get_status(),
                "package_status": "godmode_remediation_ready",
            },
        }



godmode_remediation_service = GodModeRemediationService()
