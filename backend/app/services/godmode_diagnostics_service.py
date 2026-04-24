from __future__ import annotations

from typing import Any, Dict, List

from app.services.operator_action_journal_service import operator_action_journal_service
from app.services.operator_chat_runtime_snapshot_service import operator_chat_runtime_snapshot_service
from app.services.operator_pending_attention_service import operator_pending_attention_service
from app.services.provider_connector_registry_service import provider_connector_registry_service
from app.services.secret_vault_service import secret_vault_service
from app.services.tenant_partition_service import tenant_partition_service


class GodModeDiagnosticsService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "godmode_diagnostics_status",
            "status": "godmode_diagnostics_ready",
        }

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        tenant_result = tenant_partition_service.list_tenants()
        tenant_records = tenant_result.get("tenants", [])
        provider_registry = provider_connector_registry_service.list_providers()
        vault_status = secret_vault_service.list_secrets()
        attention = operator_pending_attention_service.build_attention_feed(tenant_id=tenant_id)
        snapshot = operator_chat_runtime_snapshot_service.build_snapshot(tenant_id=tenant_id)
        journal = operator_action_journal_service.list_entries(tenant_id=tenant_id, limit=100)

        entries: List[Dict[str, Any]] = journal.get("entries", [])
        failed_events = [item for item in entries if item.get("outcome") in {"failed", "error", "restart_required"}]
        replay_events = [item for item in entries if item.get("event_type") in {"offline_queue_flushed", "replay_resumed", "provider_session_restarted"}]
        queue_events = [item for item in entries if item.get("event_type") in {"offline_queue_enqueued", "offline_queue_flushed"}]

        diagnostics = [
            {
                "diagnostic_id": "pending-attention",
                "label": "Pendências por thread",
                "severity": "warning" if attention.get("waiting_thread_count", 0) else "ok",
                "value": attention.get("waiting_thread_count", 0),
                "summary": f"{attention.get('pending_gate_count', 0)} approvals e {attention.get('pending_input_count', 0)} inputs pendentes.",
            },
            {
                "diagnostic_id": "vault-readiness",
                "label": "Secrets no vault",
                "severity": "ok" if vault_status.get("secret_count", 0) else "warning",
                "value": vault_status.get("secret_count", 0),
                "summary": "Mostra quantos secrets já estão guardados e disponíveis para deploy e runtime.",
            },
            {
                "diagnostic_id": "provider-registry",
                "label": "Providers mapeados",
                "severity": "ok" if provider_registry.get("provider_count", 0) >= 3 else "warning",
                "value": provider_registry.get("provider_count", 0),
                "summary": "Garante base mínima para GitHub, deploy providers e integrações partilhadas.",
            },
            {
                "diagnostic_id": "tenant-scope",
                "label": "Tenants registados",
                "severity": "ok" if len(tenant_records) else "warning",
                "value": len(tenant_records),
                "summary": "Mostra se já existe separação operacional suficiente para owner, clientes e familiares.",
            },
            {
                "diagnostic_id": "recent-failures",
                "label": "Falhas recentes",
                "severity": "danger" if failed_events else "ok",
                "value": len(failed_events),
                "summary": "Conta eventos operacionais marcados como falha, erro ou restart obrigatório.",
            },
            {
                "diagnostic_id": "recovery-events",
                "label": "Recuperações recentes",
                "severity": "ok",
                "value": len(replay_events),
                "summary": "Mostra replay, flush e restart feitos para recuperar o fluxo.",
            },
        ]

        blockers = []
        if provider_registry.get("provider_count", 0) < 3:
            blockers.append("Faltam providers mínimos para fluxo completo de criação/deploy de projetos.")
        if vault_status.get("secret_count", 0) == 0:
            blockers.append("Ainda não existem secrets registados no vault para automação real.")
        if attention.get("waiting_thread_count", 0) > 0:
            blockers.append("Existem threads pendentes que ainda precisam de decisão ou input do operador.")

        return {
            "ok": True,
            "mode": "godmode_diagnostics_dashboard",
            "dashboard_status": "godmode_diagnostics_dashboard_ready",
            "tenant_id": tenant_id,
            "diagnostics": diagnostics,
            "blocker_count": len(blockers),
            "blockers": blockers,
            "recent_failures": failed_events[:20],
            "recent_recoveries": replay_events[:20],
            "recent_queue_activity": queue_events[:20],
            "attention": attention,
            "snapshot_summary": {
                "thread_count": snapshot.get("thread_count", 0),
                "journal_entry_count": snapshot.get("journal_entry_count", 0),
                "pending_gate_count": snapshot.get("pending_gate_count", 0),
                "pending_input_count": snapshot.get("pending_input_count", 0),
            },
            "provider_count": provider_registry.get("provider_count", 0),
            "secret_count": vault_status.get("secret_count", 0),
            "tenant_count": len(tenant_records),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "godmode_diagnostics_package",
            "package": {
                "status": self.get_status(),
                "package_status": "godmode_diagnostics_ready",
            },
        }



godmode_diagnostics_service = GodModeDiagnosticsService()
