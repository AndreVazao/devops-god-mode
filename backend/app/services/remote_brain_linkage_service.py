from typing import Any, Dict, List


class RemoteBrainLinkageService:
    def get_linkages(self) -> Dict[str, Any]:
        linkages: List[Dict[str, Any]] = [
            {
                "remote_brain_linkage_id": "remote_brain_linkage_android_primary_01",
                "client_type": "apk_thin_client",
                "backend_role": "pc_brain",
                "voice_intent_mode": "capture_send_interpret_confirm",
                "linkage_status": "brain_link_ready",
            },
            {
                "remote_brain_linkage_id": "remote_brain_linkage_desktop_secondary_01",
                "client_type": "desktop_web_client",
                "backend_role": "pc_brain",
                "voice_intent_mode": "direct_command_contextual_response",
                "linkage_status": "brain_link_ready",
            },
        ]
        return {"ok": True, "mode": "remote_brain_linkages", "linkages": linkages}

    def get_intents(self, source_channel: str | None = None) -> Dict[str, Any]:
        intents: List[Dict[str, Any]] = [
            {
                "remote_brain_intent_id": "remote_brain_intent_voice_01",
                "source_channel": "android_voice",
                "interpreted_action": "link_conversations_and_open_repo",
                "probable_target_type": "repo_or_project",
                "confirmation_mode": "compact_voice_or_tap",
                "intent_status": "awaiting_confirmation",
            },
            {
                "remote_brain_intent_id": "remote_brain_intent_voice_02",
                "source_channel": "android_voice",
                "interpreted_action": "start_new_project_and_prepare_repo",
                "probable_target_type": "new_project",
                "confirmation_mode": "compact_voice_or_tap",
                "intent_status": "awaiting_confirmation",
            },
            {
                "remote_brain_intent_id": "remote_brain_intent_chat_01",
                "source_channel": "desktop_text",
                "interpreted_action": "audit_current_repo_and_continue",
                "probable_target_type": "existing_repo",
                "confirmation_mode": "single_confirm",
                "intent_status": "ready",
            },
        ]
        if source_channel:
            intents = [item for item in intents if item["source_channel"] == source_channel]
        return {"ok": True, "mode": "remote_brain_intents", "intents": intents}

    def get_linkage_package(self, source_channel: str) -> Dict[str, Any]:
        intents = self.get_intents(source_channel)["intents"]
        linkage = next(
            (
                item
                for item in self.get_linkages()["linkages"]
                if item["client_type"] == "apk_thin_client" and source_channel.startswith("android")
            ),
            self.get_linkages()["linkages"][0],
        )
        package = {
            "linkage": linkage,
            "intents": intents,
            "mobile_compact": True,
            "package_status": linkage["linkage_status"],
        }
        return {"ok": True, "mode": "remote_brain_linkage_package", "package": package}

    def get_next_linkage_action(self) -> Dict[str, Any]:
        intents = self.get_intents()["intents"]
        next_intent = next(
            (item for item in intents if item["intent_status"] == "awaiting_confirmation"),
            intents[0] if intents else None,
        )
        return {
            "ok": True,
            "mode": "next_remote_brain_action",
            "next_linkage_action": {
                "remote_brain_intent_id": next_intent["remote_brain_intent_id"],
                "source_channel": next_intent["source_channel"],
                "action": "interpret_in_pc_brain_and_return_compact_options",
                "intent_status": next_intent["intent_status"],
            }
            if next_intent
            else None,
        }


remote_brain_linkage_service = RemoteBrainLinkageService()
