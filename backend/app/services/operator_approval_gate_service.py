from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List


class OperatorApprovalGateService:
    def __init__(self, store_path: str = "data/operator_approval_gates.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"gates": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_approval_gate_status",
            "store_path": str(self.store_path),
            "gate_count": len(store.get("gates", [])),
            "status": "operator_approval_gate_ready",
        }

    def create_gate(
        self,
        tenant_id: str,
        thread_id: str,
        action_label: str,
        action_scope: str,
        action_payload_summary: str,
        risk_level: str = "medium",
    ) -> Dict[str, Any]:
        store = self._read_store()
        gate_id = f"gate-{len(store.get('gates', [])) + 1:05d}"
        gate = {
            "gate_id": gate_id,
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "action_label": action_label,
            "action_scope": action_scope,
            "action_payload_summary": action_payload_summary,
            "risk_level": risk_level,
            "status": "awaiting_operator_decision",
            "created_at": datetime.now(UTC).isoformat(),
            "resolved_at": None,
            "decision": None,
        }
        gates = store.get("gates", [])
        gates.append(gate)
        store["gates"] = gates
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_approval_gate_create_result",
            "create_status": "approval_gate_created",
            "gate": gate,
        }

    def resolve_gate(self, gate_id: str, decision: str) -> Dict[str, Any]:
        store = self._read_store()
        gates: List[Dict[str, Any]] = store.get("gates", [])
        gate = next((item for item in gates if item.get("gate_id") == gate_id), None)
        if gate is None:
            return {
                "ok": False,
                "mode": "operator_approval_gate_resolve_result",
                "resolve_status": "gate_not_found",
                "gate_id": gate_id,
            }
        normalized = decision.lower().strip()
        gate["decision"] = normalized
        gate["status"] = "approved" if normalized == "approve" else "denied"
        gate["resolved_at"] = datetime.now(UTC).isoformat()
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_approval_gate_resolve_result",
            "resolve_status": gate["status"],
            "gate_id": gate_id,
            "decision": normalized,
        }

    def list_gates(self, tenant_id: str | None = None, thread_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        gates = store.get("gates", [])
        if tenant_id:
            gates = [item for item in gates if item.get("tenant_id") == tenant_id]
        if thread_id:
            gates = [item for item in gates if item.get("thread_id") == thread_id]
        return {
            "ok": True,
            "mode": "operator_approval_gate_list_result",
            "gate_count": len(gates),
            "gates": gates,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_approval_gate_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_approval_gate_ready",
            },
        }


operator_approval_gate_service = OperatorApprovalGateService()
