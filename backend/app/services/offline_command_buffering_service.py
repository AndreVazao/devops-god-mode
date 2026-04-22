import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class OfflineCommandBufferingService:
    def __init__(self, storage_path: str = "data/offline_command_buffers.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if self.storage_path.exists():
            return
        self._write_store(
            {
                "connectivity": {
                    "pc_online": True,
                    "phone_online": True,
                    "last_sync_at": None,
                },
                "commands": [],
            }
        )

    def _read_store(self) -> Dict[str, Any]:
        self._ensure_store()
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

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
        store = self._read_store()
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
        with self._lock:
            store = self._read_store()
            store["connectivity"] = {
                "pc_online": bool(pc_online),
                "phone_online": bool(phone_online),
                "last_sync_at": store.get("connectivity", {}).get("last_sync_at"),
            }
            self._write_store(store)
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

        with self._lock:
            store = self._read_store()
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
                "created_at": self._now(),
                "updated_at": self._now(),
            }
            store.setdefault("commands", []).append(item)
            self._write_store(store)

        return {
            "ok": True,
            "mode": "offline_command_queued",
            "command": item,
        }

    def sync_buffered_commands_to_pc(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            connectivity = store.get("connectivity", {})
            if not bool(connectivity.get("pc_online", False)):
                return {
                    "ok": False,
                    "mode": "offline_command_sync",
                    "message": "PC offline. Os pedidos continuam guardados no telefone.",
                    "synced_count": 0,
                }

            synced_count = 0
            for item in store.get("commands", []):
                if item.get("sync_status") == "buffered_on_phone_until_pc_returns":
                    item["sync_status"] = "ready_for_pc_execution"
                    item["updated_at"] = self._now()
                    synced_count += 1

            store.setdefault("connectivity", {})["last_sync_at"] = self._now()
            self._write_store(store)

        return {
            "ok": True,
            "mode": "offline_command_sync",
            "message": "Pedidos do telefone preparados para execução no PC.",
            "synced_count": synced_count,
            "connectivity": self.get_connectivity()["connectivity"],
        }

    def mark_command_execution(
        self,
        command_id: str,
        execution_status: str,
        requires_clarification: bool = False,
    ) -> Dict[str, Any]:
        allowed_statuses = {
            "queued",
            "executing",
            "waiting_for_clarification",
            "completed",
            "paused",
        }
        if execution_status not in allowed_statuses:
            raise ValueError("invalid_execution_status")

        with self._lock:
            store = self._read_store()
            for item in store.get("commands", []):
                if item.get("command_id") != command_id:
                    continue
                item["execution_status"] = execution_status
                item["requires_clarification"] = bool(requires_clarification)
                if execution_status in {
                    "executing",
                    "waiting_for_clarification",
                    "completed",
                }:
                    item["sync_status"] = "synced_to_pc"
                item["updated_at"] = self._now()
                self._write_store(store)
                return {
                    "ok": True,
                    "mode": "offline_command_execution_marked",
                    "command": item,
                }

        raise ValueError("command_not_found")

    def get_commands(self, sync_status: Optional[str] = None) -> Dict[str, Any]:
        store = self._read_store()
        commands = self._ordered_commands(store.get("commands", []))
        if sync_status:
            commands = [item for item in commands if item.get("sync_status") == sync_status]
        return {
            "ok": True,
            "mode": "offline_command_queue",
            "count": len(commands),
            "commands": commands,
        }

    def get_buffers(self) -> Dict[str, Any]:
        connectivity = self.get_connectivity()["connectivity"]
        commands = self.get_commands()["commands"]
        phone_buffered = [
            item
            for item in commands
            if item.get("sync_status") == "buffered_on_phone_until_pc_returns"
        ]
        pc_ready = [
            item
            for item in commands
            if item.get("sync_status") in {"ready_for_pc_execution", "synced_to_pc"}
        ]
        buffers: List[Dict[str, Any]] = [
            {
                "offline_command_buffer_id": "offline_buffer_phone_01",
                "buffer_side": "phone",
                "buffer_scope": "orders_captured_while_pc_offline",
                "replay_mode": "send_when_pc_returns_then_wait_for_pc_order",
                "buffer_status": "buffer_ready",
                "pending_commands": len(phone_buffered),
                "link_mode": connectivity["link_mode"],
            },
            {
                "offline_command_buffer_id": "offline_buffer_pc_01",
                "buffer_side": "pc",
                "buffer_scope": "autonomous_execution_until_blocked_or_finished",
                "replay_mode": "continue_without_phone_when_pc_is_online",
                "buffer_status": "buffer_ready",
                "pending_commands": len(pc_ready),
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
                "recovery_mode": "ordered_replay_to_pc_queue",
                "action_status": "ready" if connectivity["pc_online"] else "waiting_for_pc",
            },
            {
                "offline_buffer_action_id": "offline_buffer_action_continue_01",
                "buffer_area": "pc_autonomous_execution",
                "action_type": "continue_current_task_without_phone",
                "action_label": "Continuar tarefa atual no PC sem telefone",
                "recovery_mode": "continue_until_completion_or_clarification",
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
            "connectivity": self.get_connectivity()["connectivity"],
            "mobile_compact": True,
            "package_status": "buffer_ready",
        }
        return {"ok": True, "mode": "offline_command_buffer_package", "package": package}

    def get_next_buffer_action(self) -> Dict[str, Any]:
        actions = self.get_buffer_actions()["actions"]
        next_action = next(
            (item for item in actions if item.get("action_status") == "ready"),
            actions[0] if actions else None,
        )
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
