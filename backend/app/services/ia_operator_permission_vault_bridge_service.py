from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.autonomous_ia_work_session_operator_service import autonomous_ia_work_session_operator_service
from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.god_mode_self_diagnosis_mission_control_service import god_mode_self_diagnosis_mission_control_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BRIDGE_FILE = DATA_DIR / "ia_operator_permission_vault_bridge.json"
BRIDGE_STORE = AtomicJsonStore(
    BRIDGE_FILE,
    default_factory=lambda: {"version": 1, "autonomous_loops": [], "bridge_events": [], "packet_bindings": []},
)

LOOP_STATUSES = {"created", "diagnosed", "packets_created", "vault_bound", "waiting_mobile_permission", "waiting_provider_response", "response_imported", "tasks_created", "blocked_needs_oner", "done"}


class IaOperatorPermissionVaultBridgeService:
    SERVICE_ID = "ia_operator_permission_vault_bridge"
    VERSION = "phase_206_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = BRIDGE_STORE.load()
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "store_file": str(BRIDGE_FILE), "autonomous_loop_count": len(state.get("autonomous_loops", [])), "packet_binding_count": len(state.get("packet_bindings", [])), "can_start_first_autonomous_work_loop": True, "can_use_vault_references": True, "can_request_mobile_permission": True, "can_apply_code_without_pr": False, "can_merge_without_oner_approval": False}

    def policy(self) -> Dict[str, Any]:
        return {"ok": True, "policy": {"principle": "Bridge IA work packets with mobile permission requests and local vault references so the PC can keep working while Oner is away.", "allowed": ["start safe autonomous God Mode work loop", "run self diagnosis and create IA work packets", "bind packets to existing vault references", "create mobile permission requests when access material is missing", "wait for mobile approval/offline resend", "import provider response and convert to review tasks"], "blocked": ["provider private login automation", "persist sensitive access material outside local vault", "paid calls without gate", "apply patches without PR", "merge/release/deploy without Oner approval"], "loop_statuses": sorted(LOOP_STATUSES)}}

    def start_first_autonomous_work_loop(self, goal: str = "Make God Mode installable, usable and self-improving on the home PC.", project_id: str = "GOD_MODE", providers: List[str] | None = None, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        providers = providers or ["chatgpt", "claude", "gemini"]
        loop = {"autonomous_loop_id": f"autonomous-loop-{uuid4().hex[:12]}", "created_at": self._now(), "updated_at": self._now(), "tenant_id": tenant_id, "project_id": project_id, "goal": self._sanitize(goal)[:1200], "providers": providers, "status": "created", "safe_mode": True, "requires_oner_for": ["merge", "release", "deploy", "paid_api", "access_material_creation", "browser_login"]}
        self._store("autonomous_loops", loop)
        diagnosis = god_mode_self_diagnosis_mission_control_service.run_diagnosis(tenant_id=tenant_id, focus="first_autonomous_work_loop")
        self._update_loop(loop["autonomous_loop_id"], {"status": "diagnosed", "diagnostic_run_id": diagnosis.get("diagnostic_run", {}).get("diagnostic_run_id"), "updated_at": self._now()})
        session = autonomous_ia_work_session_operator_service.create_session(title="God Mode first autonomous self-work loop", goal=goal, project_id=project_id, operator_mode="oner_busy_safe", tenant_id=tenant_id)
        work_session_id = session.get("work_session", {}).get("work_session_id")
        packet_result = autonomous_ia_work_session_operator_service.create_packets_from_self_diagnosis(work_session_id=work_session_id, providers=providers, limit=5, tenant_id=tenant_id) if work_session_id else {"ok": False, "work_packets": []}
        packets = packet_result.get("work_packets", [])
        bindings = [self.bind_packet_to_vault_or_permission(packet.get("work_packet_id"), tenant_id=tenant_id) for packet in packets if packet.get("work_packet_id")]
        final_status = "waiting_mobile_permission" if any(binding.get("permission_request") for binding in bindings) else "vault_bound"
        self._update_loop(loop["autonomous_loop_id"], {"status": final_status, "work_session_id": work_session_id, "work_packet_ids": [packet.get("work_packet_id") for packet in packets], "updated_at": self._now()})
        return {"ok": True, "mode": "first_autonomous_work_loop", "autonomous_loop": self._find_loop(loop["autonomous_loop_id"]), "diagnosis": diagnosis, "work_session": session.get("work_session"), "work_packets": packets, "packet_bindings": bindings}

    def bind_packet_to_vault_or_permission(self, work_packet_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        packets = autonomous_ia_work_session_operator_service.list_packets(limit=500).get("work_packets", [])
        packet = next((item for item in packets if item.get("work_packet_id") == work_packet_id), None)
        if not packet:
            return {"ok": False, "mode": "bind_packet_to_vault_or_permission", "error": "work_packet_not_found", "work_packet_id": work_packet_id}
        provider = packet.get("provider") or "manual_ai"
        project_id = packet.get("target_project") or "GOD_MODE"
        refs = god_mode_local_vault_service.list_references(provider=provider, project_id=project_id, limit=10).get("vault_references", [])
        binding = {"packet_binding_id": f"packet-binding-{uuid4().hex[:12]}", "created_at": self._now(), "tenant_id": tenant_id, "work_packet_id": work_packet_id, "provider": provider, "project_id": project_id, "vault_references": refs, "permission_request_id": None, "status": "vault_bound" if refs else "permission_required", "can_continue_without_oner": bool(refs)}
        permission = None
        if not refs:
            permission = mobile_permission_relay_driver_voice_service.create_permission_request(title=f"Acesso necessário para {provider}", body=f"O God Mode precisa de material de acesso para continuar o packet: {packet.get('task_title')}. Se estiveres a conduzir, fica em espera até poderes aprovar/preencher.", request_type="sensitive_fill", project_id=project_id, source_ref={"type": "ia_work_packet", "work_packet_id": work_packet_id, "provider": provider}, priority="high", requires_sensitive_input=True, form_schema=[{"name": "secure_value", "label": f"Valor de acesso para {provider}", "type": "text", "required": True, "sensitive": True}], wait_for_response=True, tenant_id=tenant_id)
            binding["permission_request_id"] = permission.get("permission_request", {}).get("permission_request_id")
        self._store("packet_bindings", binding)
        return {"ok": True, "mode": "bind_packet_to_vault_or_permission", "packet_binding": binding, "permission_request": permission}

    def ingest_provider_response_and_continue(self, work_packet_id: str, response_text: str, provider: str = "manual_ai", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        imported = autonomous_ia_work_session_operator_service.import_response(work_packet_id=work_packet_id, response_text=response_text, provider=provider, tenant_id=tenant_id)
        tasks = autonomous_ia_work_session_operator_service.convert_response_to_tasks(work_packet_id=work_packet_id, tenant_id=tenant_id) if imported.get("ok") else {"ok": False}
        self._store("bridge_events", {"bridge_event_id": f"bridge-event-{uuid4().hex[:12]}", "created_at": self._now(), "tenant_id": tenant_id, "event": "response_imported_and_tasks_created", "work_packet_id": work_packet_id, "provider": provider})
        return {"ok": bool(imported.get("ok")), "mode": "ingest_provider_response_and_continue", "imported": imported, "tasks": tasks}

    def dashboard(self) -> Dict[str, Any]:
        state = BRIDGE_STORE.load()
        return {"ok": True, "mode": "ia_operator_permission_vault_bridge_dashboard", "status": self.status(), "policy": self.policy(), "autonomous_loops": state.get("autonomous_loops", [])[-100:], "packet_bindings": state.get("packet_bindings", [])[-200:], "bridge_events": state.get("bridge_events", [])[-200:]}

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _find_loop(self, autonomous_loop_id: str) -> Dict[str, Any] | None:
        return next((item for item in BRIDGE_STORE.load().get("autonomous_loops", []) if item.get("autonomous_loop_id") == autonomous_loop_id), None)

    def _update_loop(self, autonomous_loop_id: str, patch: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for loop in state.get("autonomous_loops", []):
                if loop.get("autonomous_loop_id") == autonomous_loop_id:
                    loop.update(patch)
            return state
        BRIDGE_STORE.update(mutate)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-2000:]
            return state
        BRIDGE_STORE.update(mutate)

    def _sanitize(self, text: str) -> str:
        return (text or "").replace("api_key=", "[REDACTED]=")[:4000]


ia_operator_permission_vault_bridge_service = IaOperatorPermissionVaultBridgeService()
