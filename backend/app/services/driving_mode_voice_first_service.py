from typing import Any, Dict, List

from app.services.mobile_cockpit_command_surface_service import (
    mobile_cockpit_command_surface_service,
)


class DrivingModeVoiceFirstService:
    def _guards(self) -> List[Dict[str, Any]]:
        quick_actions = mobile_cockpit_command_surface_service.get_quick_actions()[
            "quick_actions"
        ]
        guards: List[Dict[str, Any]] = []
        for action in quick_actions:
            risk_level = "low"
            requires_voice_confirmation = False
            allowed_in_safe_mode = True

            if action["action_type"] == "advance_browser_action":
                risk_level = "medium"
                requires_voice_confirmation = True
            elif action["action_type"] == "continue_intake":
                risk_level = "low"
                requires_voice_confirmation = False

            guards.append(
                {
                    "guard_id": f"guard_{action['action_id']}",
                    "action_id": action["action_id"],
                    "risk_level": risk_level,
                    "requires_voice_confirmation": requires_voice_confirmation,
                    "allowed_in_safe_mode": allowed_in_safe_mode,
                    "guard_status": "guard_ready",
                }
            )
        return guards

    def get_summary(self) -> Dict[str, Any]:
        next_action = mobile_cockpit_command_surface_service.get_next_critical_action()[
            "next_critical_action"
        ]
        guards = self._guards()
        next_guard = (
            next((guard for guard in guards if next_action and guard["action_id"] == next_action["action_id"]), None)
            if next_action
            else None
        )
        spoken_text = (
            "Tens uma ação segura pronta. Responde sim para avançar ou não para manter em espera."
            if next_action and (next_guard is None or next_guard["allowed_in_safe_mode"])
            else "Sem ação segura pronta. Mantém o modo resumido ativo."
        )
        return {
            "ok": True,
            "mode": "driving_mode_summary",
            "summary": {
                "voice_mode": "safe_short_prompts",
                "spoken_text": spoken_text,
                "next_action_id": next_action["action_id"] if next_action else None,
                "risk_level": next_guard["risk_level"] if next_guard else None,
                "summary_status": "driving_mode_ready",
            },
        }

    def get_prompts(self) -> Dict[str, Any]:
        next_action = mobile_cockpit_command_surface_service.get_next_critical_action()[
            "next_critical_action"
        ]
        guards = self._guards()
        prompts: List[Dict[str, Any]] = []
        if next_action:
            guard = next(
                (item for item in guards if item["action_id"] == next_action["action_id"]),
                None,
            )
            prompts.append(
                {
                    "prompt_id": "prompt_next_safe_action",
                    "prompt_type": "next_action",
                    "spoken_text": (
                        f"A próxima ação é {next_action['label']}. "
                        + (
                            "Diz sim para confirmar."
                            if guard and guard["requires_voice_confirmation"]
                            else "Está pronta para avanço rápido."
                        )
                    ),
                    "expected_reply_mode": "yes_no",
                    "priority": "high",
                    "prompt_status": "ready",
                }
            )
        else:
            prompts.append(
                {
                    "prompt_id": "prompt_no_action",
                    "prompt_type": "idle",
                    "spoken_text": "Não há ação crítica pronta neste momento.",
                    "expected_reply_mode": "none",
                    "priority": "low",
                    "prompt_status": "ready",
                }
            )
        return {"ok": True, "mode": "driving_mode_prompts", "prompts": prompts}

    def get_action_guards(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "driving_action_guards",
            "guards": self._guards(),
        }

    def get_next_safe_action(self) -> Dict[str, Any]:
        next_action = mobile_cockpit_command_surface_service.get_next_critical_action()[
            "next_critical_action"
        ]
        guards = self._guards()
        safe_action = None
        if next_action:
            guard = next(
                (item for item in guards if item["action_id"] == next_action["action_id"]),
                None,
            )
            if guard and guard["allowed_in_safe_mode"]:
                safe_action = {
                    "action_id": next_action["action_id"],
                    "label": next_action["label"],
                    "requires_voice_confirmation": guard[
                        "requires_voice_confirmation"
                    ],
                    "risk_level": guard["risk_level"],
                }
        return {
            "ok": True,
            "mode": "driving_mode_next_safe_action",
            "next_safe_action": safe_action,
        }

    def confirm_short_action(self, reply: str) -> Dict[str, Any]:
        normalized = reply.strip().lower()
        if normalized not in {"sim", "nao", "não"}:
            raise ValueError("invalid_reply")

        next_action = self.get_next_safe_action()["next_safe_action"]
        if not next_action:
            return {
                "ok": True,
                "mode": "driving_mode_action_confirmation",
                "result": "no_safe_action_available",
            }

        if normalized in {"nao", "não"}:
            return {
                "ok": True,
                "mode": "driving_mode_action_confirmation",
                "result": "action_kept_pending",
                "action_id": next_action["action_id"],
            }

        advanced = mobile_cockpit_command_surface_service.advance_quick_action(
            next_action["action_id"]
        )
        return {
            "ok": True,
            "mode": "driving_mode_action_confirmation",
            "result": "action_advanced",
            "action_id": next_action["action_id"],
            "advanced": advanced,
        }


driving_mode_voice_first_service = DrivingModeVoiceFirstService()
