from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PRIORITY_FILE = DATA_DIR / "operator_project_priorities.json"
PRIORITY_STORE = AtomicJsonStore(
    PRIORITY_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "operator_order_first_money_is_consequence",
        "active_project": "GOD_MODE",
        "projects": [
            {"project_id": "GOD_MODE", "label": "God Mode", "priority": 1, "enabled": True},
            {"project_id": "BARIBUDOS_STUDIO", "label": "Baribudos Studio", "priority": 2, "enabled": True},
            {"project_id": "BARIBUDOS_STUDIO_WEBSITE", "label": "Baribudos Studio Website", "priority": 3, "enabled": True},
            {"project_id": "PROVENTIL", "label": "ProVentil", "priority": 4, "enabled": True},
            {"project_id": "VERBAFORGE", "label": "VerbaForge", "priority": 5, "enabled": True},
            {"project_id": "BOT_FACTORY", "label": "Bot Factory", "priority": 6, "enabled": True},
            {"project_id": "BOT_LORDS_MOBILE", "label": "Bot Lords Mobile", "priority": 7, "enabled": True},
            {"project_id": "ECU_REPRO", "label": "ECU Repro", "priority": 8, "enabled": True},
            {"project_id": "BUILD_CONTROL_CENTER", "label": "Build Control Center", "priority": 9, "enabled": True},
        ],
        "history": [],
    },
)


class OperatorPriorityService:
    """Operator-defined project priority policy.

    Money is not the planner's primary goal here. The backend must obey the
    operator-selected project order and treat revenue as a consequence of fixing
    and shipping the requested projects.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("policy", "operator_order_first_money_is_consequence")
        payload.setdefault("active_project", "GOD_MODE")
        payload.setdefault("projects", [])
        payload.setdefault("history", [])
        for index, item in enumerate(payload["projects"], start=1):
            item.setdefault("project_id", f"PROJECT_{index}")
            item.setdefault("label", item["project_id"])
            item.setdefault("priority", index)
            item.setdefault("enabled", True)
        payload["projects"] = sorted(payload["projects"], key=lambda item: int(item.get("priority", 9999)))
        enabled = [item for item in payload["projects"] if item.get("enabled", True)]
        if enabled and payload.get("active_project") not in {item["project_id"] for item in enabled}:
            payload["active_project"] = enabled[0]["project_id"]
        return payload

    def _load(self) -> Dict[str, Any]:
        return self._normalize(PRIORITY_STORE.load())

    def get_status(self) -> Dict[str, Any]:
        state = self._load()
        enabled = [item for item in state["projects"] if item.get("enabled", True)]
        return {
            "ok": True,
            "mode": "operator_priority_status",
            "policy": state["policy"],
            "active_project": state["active_project"],
            "enabled_count": len(enabled),
            "project_count": len(state["projects"]),
            "top_project": enabled[0] if enabled else None,
            "money_priority_enabled": False,
        }

    def get_priorities(self) -> Dict[str, Any]:
        state = self._load()
        return {"ok": True, "mode": "operator_priority_list", "state": state}

    def set_order(self, ordered_project_ids: List[str], active_project: str | None = None, note: str | None = None) -> Dict[str, Any]:
        clean_order = [item.strip().upper() for item in ordered_project_ids if item and item.strip()]
        if not clean_order:
            raise ValueError("empty_project_order")

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._normalize(state)
            existing = {item["project_id"]: item for item in state["projects"]}
            projects: List[Dict[str, Any]] = []
            used = set()
            for index, project_id in enumerate(clean_order, start=1):
                item = dict(existing.get(project_id, {"project_id": project_id, "label": project_id.replace("_", " ").title(), "enabled": True}))
                item["priority"] = index
                item["enabled"] = True
                projects.append(item)
                used.add(project_id)
            next_priority = len(projects) + 1
            for project_id, item in existing.items():
                if project_id in used:
                    continue
                clone = dict(item)
                clone["priority"] = next_priority
                next_priority += 1
                projects.append(clone)
            state["projects"] = projects
            state["active_project"] = active_project.upper() if active_project else clean_order[0]
            state["history"].append({
                "created_at": self._now(),
                "event": "set_order",
                "ordered_project_ids": clean_order,
                "active_project": state["active_project"],
                "note": note or "operator priority updated",
            })
            state["history"] = state["history"][-100:]
            return self._normalize(state)

        updated = PRIORITY_STORE.update(mutate)
        return {"ok": True, "mode": "operator_priority_set_order", "state": updated}

    def set_active_project(self, project_id: str, note: str | None = None) -> Dict[str, Any]:
        target = project_id.strip().upper()
        if not target:
            raise ValueError("empty_project_id")

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._normalize(state)
            known = {item["project_id"] for item in state["projects"]}
            if target not in known:
                state["projects"].append({
                    "project_id": target,
                    "label": target.replace("_", " ").title(),
                    "priority": len(state["projects"]) + 1,
                    "enabled": True,
                })
            state["active_project"] = target
            state["history"].append({
                "created_at": self._now(),
                "event": "set_active_project",
                "active_project": target,
                "note": note or "operator selected active project",
            })
            state["history"] = state["history"][-100:]
            return self._normalize(state)

        updated = PRIORITY_STORE.update(mutate)
        return {"ok": True, "mode": "operator_priority_set_active", "state": updated}

    def resolve_project(self, requested_project: str | None = None) -> Dict[str, Any]:
        state = self._load()
        projects = [item for item in state["projects"] if item.get("enabled", True)]
        if requested_project:
            target = requested_project.strip().upper()
            for item in projects:
                if item["project_id"] == target or item["label"].strip().upper() == target:
                    return {"ok": True, "mode": "operator_priority_resolve", "project": item, "source": "explicit_request"}
            return {"ok": True, "mode": "operator_priority_resolve", "project": {"project_id": target, "label": target.replace("_", " ").title(), "priority": 999, "enabled": True}, "source": "explicit_unknown_added_by_request"}
        active = state.get("active_project")
        for item in projects:
            if item["project_id"] == active:
                return {"ok": True, "mode": "operator_priority_resolve", "project": item, "source": "active_project"}
        if projects:
            return {"ok": True, "mode": "operator_priority_resolve", "project": projects[0], "source": "top_enabled"}
        return {"ok": False, "mode": "operator_priority_resolve", "project": None, "source": "none"}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "operator_priority_package", "package": {"status": self.get_status(), "priorities": self.get_priorities()}}


operator_priority_service = OperatorPriorityService()
