from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.request_orchestrator_service import request_orchestrator_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
OFFLINE_BUFFER_FILE = DATA_DIR / "offline_command_buffers.json"
OFFLINE_BUFFER_STORE = AtomicJsonStore(
    OFFLINE_BUFFER_FILE,
    default_factory=lambda: {
        "connectivity": {"pc_online": True, "phone_online": True, "last_sync_at": None},
        "commands": [],
        "replays": [],
    },
)

SENSITIVE_WORDS = {"token", "password", "passwd", "secret", "api_key", "apikey", "authorization", "bearer", "cookie"}


class OfflineCommandBufferingService:
    """Persistent local-first offline command buffer.

    Phone can queue commands while PC is offline. When PC returns, commands replay
    into the durable Request Orchestrator, which continues until blocked or done.
    """

    def __init__(self, storage_path: str = "data/offline_command_buffers.json") -> None:
        self.storage_path = Path(storage_path)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            store = {}
        store.setdefault("connectivity", {"pc_online": True, "phone_online": True, "last_sync_at": None})
        store.setdefault("commands", [])
        store.setdefault("replays", [])
        store["connectivity"].setdefault("pc_online", True)
        store["connectivity"].setdefault("phone_online", True)
        store["connectivity"].setdefault("last_sync_at", None)
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(OFFLINE_BUFFER_STORE.load())

    def _save_with(self, mutator: Any) -> Dict[str, Any]:
        def wrapped(store: Dict[str, Any]) -> Dict[str, Any]:
            normalized = self._normalize_store(store)
            updated = mutator(normalized)
            return self._normalize_store(updated if updated is not None else normalized)

        updated = OFFLINE_BUFFER_STORE.update(wrapped)
        return self._normalize_store(updated.get("payload", {}))

    def _contains_sensitive_keyword(self, text: str) -> bool:
        lowered = text.lower()
        return any(re.search(rf"(?<![a-z0-9_]){re.escape(word)}(?![a-z0-9_])", lowered) for word in SENSITIVE_WORDS)

    def _link_mode(self, pc_online: bool, phone_online: bool) -> str:
        if pc_online and phone_online:
            return "both_online"
        if pc_online:
            return "pc_only"
        if phone_online:
            return "phone_only"
        return "both_offline"

    def _ordered_commands(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            commands,
            key=lambda item: (
                item.get("execution_status") == "completed",
                item.get("created_at") or "",
            ),
        )

    def get_connectivity(self) -> Dict[str, Any]:
        store = self._load_store()
        connectivity = store.get("connectivity", {})
        pc_online = bool(connectivity.get("pc_online", False))
        phone_online = bool(connectivity.get("phone_online", False))
        return {
            "ok": True,
            "mode": "offline_command_connectivity",
            "connectivity": {
                "pc_online": pc_online,
                "phone_online": phone_online,
                "last_sync_at": connectivity.get("last_sync_at"),
                "link_mode": self._link_mode(pc_online, phone_online),
            },
        }

    def set_connectivity(self, pc_online: bool, phone_online: bool) -> Dict[str, Any]:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store["connectivity"] = {
                "pc_online": bool(pc_online),
                "phone_online": bool(phone_online),
                "last_sync_at": store.get("connectivity", {}).get("last_sync_at"),
            }
            return store

        self._save_with(mutate)
        return self.get_connectivity()

    def queue_command(
        self,
        source_side: str,
        command_text: str,
        target_scope: str = "pc_primary_executor",
        autonomy_mode: str = "continue_until_blocked_or_finished",
        project_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_side = (source_side or "").strip().lower()
        if normalized_side not in {"phone", "pc"}:
            raise ValueError("invalid_source_side")
        normalized_text = (command_text or "").strip()
        if not normalized_text:
            raise ValueError("empty_command_text")
        if self._contains_sensitive_keyword(normalized_text):
            raise ValueError("sensitive_like_command_blocked")

        store = self._load_store()
        connectivity = store.get("connectivity", {})
        pc_online = bool(connectivity.get("pc_online", False))
        sync_status = "ready_for_pc_execution"
        if normalized_side == "phone" and not pc_online:
            sync_status = "buffered_on_phone_until_pc_returns"

        item = {
            "command_id": f"buffered_command_{uuid.uuid4().hex[:12]}",
            "source_side": normalized_side,
            "target_scope": target_scope,
            "project_hint": project_hint,
            "command_text": normalized_text,
            "autonomy_mode": autonomy_mode,
            "delivery_policy": "pc_executes_only_after_order",
            "execution_policy": "continue_until_blocked_or_finished",
            "sync_status": sync_status,
            "execution_status": "queued",
            "requires_clarification": False,
            "orchestrator_job_id": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload.setdefault("commands", []).append(item)
            return payload

        self._save_with(mutate)
        return {"ok": True, "mode": "offline_command_queued", "command": item}

    def sync_buffered_commands_to_pc(self) -> Dict[str, Any]:
        store = self._load_store()
        connectivity = store.get("connectivity", {})
        if not bool(connectivity.get("pc_online", False)):
            return {
                "ok": False,
                "mode": "offline_command_sync",
                "message": "PC offline. Os pedidos continuam guardados no telefone.",
                "synced_count": 0,
            }

        synced_ids: List[str] = []

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            for item in payload.get("commands", []):
                if item.get("sync_status") == "buffered_on_phone_until_pc_returns":
                    item["sync_status"] = "ready_for_pc_execution"
                    item["updated_at"] = self._now()
                    synced_ids.append(item["command_id"])
            payload.setdefault("connectivity", {})["last_sync_at"] = self._now()
            return payload

        self._save_with(mutate)
        return {
            "ok": True,
            "mode": "offline_command_sync",
            "message": "Pedidos do telefone preparados para execução no PC.",
            "synced_count": len(synced_ids),
            "synced_command_ids": synced_ids,
            "connectivity": self.get_connectivity()["connectivity"],
        }

    def replay_ready_commands_to_orchestrator(self, tenant_id: str = "owner-andre", auto_run: bool = True, max_commands: int = 10) -> Dict[str, Any]:
        store = self._load_store()
        ready = [
            item
            for item in self._ordered_commands(store.get("commands", []))
            if item.get("sync_status") == "ready_for_pc_execution"
            and item.get("execution_status") == "queued"
            and not item.get("orchestrator_job_id")
        ][: max(1, min(int(max_commands), 50))]
        results: List[Dict[str, Any]] = []
        for item in ready:
            try:
                submitted = request_orchestrator_service.submit_request(
                    request=item["command_text"],
                    tenant_id=tenant_id,
                    project_id=item.get("project_hint") or "GOD_MODE",
                    thread_id=None,
                    auto_run=auto_run,
                )
                job = submitted.get("job", {}) if submitted.get("ok") else {}
                results.append({
                    "command_id": item["command_id"],
                    "ok": bool(submitted.get("ok")),
                    "job_id": job.get("job_id"),
                    "job_status": job.get("status"),
                    "error": submitted.get("error"),
                })
            except Exception as exc:  # pragma: no cover - replay must continue per command
                results.append({"command_id": item["command_id"], "ok": False, "error": str(exc)})

        replay = {
            "replay_id": f"offline-replay-{uuid.uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "auto_run": auto_run,
            "processed_count": len(results),
            "success_count": len([item for item in results if item.get("ok")]),
            "results": results,
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            by_id = {item["command_id"]: item for item in results}
            for command in payload.get("commands", []):
                result = by_id.get(command.get("command_id"))
                if not result:
                    continue
                command["updated_at"] = self._now()
                if result.get("ok"):
                    command["sync_status"] = "synced_to_pc"
                    command["execution_status"] = result.get("job_status") or "executing"
                    command["orchestrator_job_id"] = result.get("job_id")
                else:
                    command["execution_status"] = "paused"
                    command["requires_clarification"] = True
                    command["last_error"] = result.get("error")
            payload.setdefault("replays", []).append(replay)
            payload["replays"] = payload["replays"][-300:]
            return payload

        self._save_with(mutate)
        return {"ok": True, "mode": "offline_commands_replayed_to_orchestrator", "replay": replay}

    def sync_and_replay_to_pc(self, tenant_id: str = "owner-andre", auto_run: bool = True, max_commands: int = 10) -> Dict[str, Any]:
        sync = self.sync_buffered_commands_to_pc()
        if not sync.get("ok"):
            return {"ok": False, "mode": "offline_sync_and_replay", "sync": sync, "replay": None}
        replay = self.replay_ready_commands_to_orchestrator(tenant_id=tenant_id, auto_run=auto_run, max_commands=max_commands)
        worker = request_worker_loop_service.tick(tenant_id=tenant_id, max_jobs=max_commands) if auto_run else None
        return {"ok": True, "mode": "offline_sync_and_replay", "sync": sync, "replay": replay, "worker_tick": worker}

    def mark_command_execution(self, command_id: str, execution_status: str, requires_clarification: bool = False) -> Dict[str, Any]:
        allowed_statuses = {"queued", "executing", "waiting_for_clarification", "completed", "paused", "blocked_approval", "blocked_credentials", "blocked_manual_input"}
        if execution_status not in allowed_statuses:
            raise ValueError("invalid_execution_status")
        updated_command: Dict[str, Any] | None = None

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal updated_command
            for item in payload.get("commands", []):
                if item.get("command_id") != command_id:
                    continue
                item["execution_status"] = execution_status
                item["requires_clarification"] = bool(requires_clarification)
                if execution_status in {"executing", "waiting_for_clarification", "completed", "blocked_approval", "blocked_credentials", "blocked_manual_input"}:
                    item["sync_status"] = "synced_to_pc"
                item["updated_at"] = self._now()
                updated_command = dict(item)
                break
            return payload

        self._save_with(mutate)
        if not updated_command:
            raise ValueError("command_not_found")
        return {"ok": True, "mode": "offline_command_execution_marked", "command": updated_command}

    def get_commands(self, sync_status: Optional[str] = None) -> Dict[str, Any]:
        store = self._load_store()
        commands = self._ordered_commands(store.get("commands", []))
        if sync_status:
            commands = [item for item in commands if item.get("sync_status") == sync_status]
        return {"ok": True, "mode": "offline_command_queue", "count": len(commands), "commands": commands}

    def get_replays(self, limit: int = 50) -> Dict[str, Any]:
        replays = self._load_store().get("replays", [])[-limit:]
        return {"ok": True, "mode": "offline_command_replays", "count": len(replays), "replays": replays}

    def get_buffers(self) -> Dict[str, Any]:
        connectivity = self.get_connectivity()["connectivity"]
        commands = self.get_commands()["commands"]
        phone_buffered = [item for item in commands if item.get("sync_status") == "buffered_on_phone_until_pc_returns"]
        pc_ready = [item for item in commands if item.get("sync_status") in {"ready_for_pc_execution", "synced_to_pc"}]
        replayed = [item for item in commands if item.get("orchestrator_job_id")]
        buffers: List[Dict[str, Any]] = [
            {
                "offline_command_buffer_id": "offline_buffer_phone_01",
                "buffer_side": "phone",
                "buffer_scope": "orders_captured_while_pc_offline",
                "replay_mode": "send_when_pc_returns_then_orchestrator_job",
                "buffer_status": "buffer_ready",
                "pending_commands": len(phone_buffered),
                "link_mode": connectivity["link_mode"],
            },
            {
                "offline_command_buffer_id": "offline_buffer_pc_01",
                "buffer_side": "pc",
                "buffer_scope": "autonomous_execution_until_blocked_or_finished",
                "replay_mode": "request_orchestrator_then_worker_loop",
                "buffer_status": "buffer_ready",
                "pending_commands": len(pc_ready),
                "replayed_commands": len(replayed),
                "link_mode": connectivity["link_mode"],
            },
        ]
        return {"ok": True, "mode": "offline_command_buffers", "buffers": buffers}

    def get_buffer_actions(self, buffer_area: Optional[str] = None) -> Dict[str, Any]:
        connectivity = self.get_connectivity()["connectivity"]
        actions: List[Dict[str, Any]] = [
            {
                "offline_buffer_action_id": "offline_buffer_action_replay_01",
                "buffer_area": "phone_pending_queue",
                "action_type": "replay_buffered_commands_when_pc_returns",
                "action_label": "Reenviar pedidos guardados no telefone quando o PC voltar",
                "recovery_mode": "ordered_replay_to_request_orchestrator",
                "action_status": "ready" if connectivity["pc_online"] else "waiting_for_pc",
            },
            {
                "offline_buffer_action_id": "offline_buffer_action_continue_01",
                "buffer_area": "pc_autonomous_execution",
                "action_type": "continue_current_task_without_phone",
                "action_label": "Continuar tarefa atual no PC sem telefone",
                "recovery_mode": "request_worker_loop_until_blocked_or_done",
                "action_status": "ready" if connectivity["pc_online"] else "blocked",
            },
            {
                "offline_buffer_action_id": "offline_buffer_action_sync_01",
                "buffer_area": "dual_side_recovery",
                "action_type": "sync_states_when_link_returns",
                "action_label": "Sincronizar estados quando a ligação regressar",
                "recovery_mode": "state_reconcile_then_resume",
                "action_status": "ready" if connectivity["pc_online"] and connectivity["phone_online"] else "waiting_for_link",
            },
        ]
        if buffer_area:
            actions = [item for item in actions if item.get("buffer_area") == buffer_area]
        return {"ok": True, "mode": "offline_buffer_actions", "actions": actions}

    def get_buffer_package(self) -> Dict[str, Any]:
        package = {
            "buffers": self.get_buffers()["buffers"],
            "actions": self.get_buffer_actions()["actions"],
            "commands": self.get_commands()["commands"],
            "replays": self.get_replays()["replays"],
            "connectivity": self.get_connectivity()["connectivity"],
            "mobile_compact": True,
            "atomic_store_enabled": True,
            "request_orchestrator_bridge": True,
            "package_status": "buffer_ready",
        }
        return {"ok": True, "mode": "offline_command_buffer_package", "package": package}

    def get_next_buffer_action(self) -> Dict[str, Any]:
        actions = self.get_buffer_actions()["actions"]
        next_action = next((item for item in actions if item.get("action_status") == "ready"), actions[0] if actions else None)
        return {
            "ok": True,
            "mode": "next_offline_buffer_action",
            "next_buffer_action": {
                "offline_buffer_action_id": next_action["offline_buffer_action_id"],
                "buffer_area": next_action["buffer_area"],
                "action": next_action["action_type"],
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


offline_command_buffering_service = OfflineCommandBufferingService()
