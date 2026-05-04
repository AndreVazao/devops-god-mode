from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.external_ai_browser_worker_service import external_ai_browser_worker_service
from app.services.external_ai_chat_reader_service import external_ai_chat_reader_service
from app.services.multi_ai_conversation_inventory_service import multi_ai_conversation_inventory_service

PROOF_DIR = Path("data/provider_proofs")
PROBE_TOOL = Path("tools/pc_provider_conversation_probe.py")
SUPPORTED_PROVIDERS = ["chatgpt", "claude", "gemini", "perplexity"]


class PcProviderConversationProofService:
    """First real PC proof layer for external AI conversations.

    The backend exposes commands/instructions and imports proof JSON produced by
    the local PC tool. It does not execute browser automation in CI and it never
    stores passwords/tokens/cookies.
    """

    SERVICE_ID = "pc_provider_conversation_proof"
    VERSION = "phase_180_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        proofs = self.list_proofs(limit=20)
        browser = external_ai_browser_worker_service.capability_report()
        reader = external_ai_chat_reader_service.capability_report()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "supported_providers": SUPPORTED_PROVIDERS,
            "probe_tool": str(PROBE_TOOL),
            "proof_dir": str(PROOF_DIR),
            "proof_count": proofs.get("proof_count", 0),
            "browser_worker_status": browser.get("status"),
            "reader_status": reader.get("status"),
            "stores_credentials": False,
            "requires_real_pc": True,
        }

    def install_plan(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "pc_provider_conversation_proof_install_plan",
            "steps": [
                "Open the Windows God Mode backend/launcher on the PC.",
                "Confirm /health and /app/home in the browser.",
                "Install Playwright only on the PC runtime environment if missing.",
                "Run: python -m pip install playwright",
                "Run: python -m playwright install chromium",
                "Run the probe tool for a selected provider in visible mode.",
                "Login manually in the browser window opened by the tool.",
                "Let the tool write proof JSON to data/provider_proofs.",
                "Import the proof JSON via /api/pc-provider-conversation-proof/import-latest.",
                "Review staged conversations in /api/multi-ai-conversation-inventory/package.",
            ],
            "safe_command_examples": {
                "chatgpt": "python tools/pc_provider_conversation_probe.py --provider chatgpt --wait-login-seconds 90",
                "gemini": "python tools/pc_provider_conversation_probe.py --provider gemini --wait-login-seconds 90",
                "claude": "python tools/pc_provider_conversation_probe.py --provider claude --wait-login-seconds 90",
                "perplexity": "python tools/pc_provider_conversation_probe.py --provider perplexity --wait-login-seconds 90",
            },
            "security_rules": [
                "Manual login only.",
                "Do not type credentials into God Mode chat/logs.",
                "Probe does not export cookies/tokens/passwords.",
                "Proof JSON stores only visible text/link snapshots with sensitive words redacted.",
                "Operator must review before any cleanup/delete/send action.",
            ],
        }

    def provider_proof_command(self, provider: str = "chatgpt", url: str | None = None, wait_login_seconds: int = 90) -> Dict[str, Any]:
        provider = provider.lower().strip()
        if provider not in SUPPORTED_PROVIDERS:
            return {"ok": False, "error": "unsupported_provider", "supported_providers": SUPPORTED_PROVIDERS}
        parts = ["python", str(PROBE_TOOL), "--provider", provider, "--wait-login-seconds", str(max(0, min(wait_login_seconds, 900)))]
        if url:
            parts.extend(["--url", url])
        return {
            "ok": True,
            "mode": "pc_provider_conversation_proof_command",
            "provider": provider,
            "command": " ".join(parts),
            "expected_output_dir": str(PROOF_DIR),
            "operator_next": "Run this on the PC where the browser can open visibly, then import latest proof.",
        }

    def list_proofs(self, limit: int = 50) -> Dict[str, Any]:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(PROOF_DIR.glob("*_proof_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        items: List[Dict[str, Any]] = []
        for path in files[: max(1, min(limit, 200))]:
            data = self._read_json(path)
            items.append({
                "file": str(path),
                "provider": data.get("provider"),
                "ok": data.get("ok"),
                "status": data.get("status"),
                "message_count": data.get("message_count", 0),
                "conversation_link_count": data.get("conversation_link_count", 0),
                "created_at": data.get("created_at"),
                "summary": data.get("summary", {}),
            })
        return {"ok": True, "mode": "pc_provider_conversation_proof_list", "proof_count": len(files), "proofs": items}

    def import_latest(self, tenant_id: str = "owner-andre", project_hint: str | None = None) -> Dict[str, Any]:
        listed = self.list_proofs(limit=1)
        proofs = listed.get("proofs", [])
        if not proofs:
            return {"ok": False, "error": "no_provider_proof_found", "proof_dir": str(PROOF_DIR)}
        return self.import_proof_file(proofs[0]["file"], tenant_id=tenant_id, project_hint=project_hint)

    def import_proof_file(self, proof_file: str, tenant_id: str = "owner-andre", project_hint: str | None = None) -> Dict[str, Any]:
        path = Path(proof_file)
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": "proof_file_not_found", "proof_file": proof_file}
        proof = self._read_json(path)
        if not proof.get("ok"):
            return {"ok": False, "error": "proof_not_ok", "proof_status": proof.get("status"), "proof_file": str(path)}
        provider = str(proof.get("provider") or "unknown")
        title = f"{provider} proof import: {proof.get('title') or proof.get('final_url') or 'provider conversation'}"
        snippet_parts: List[str] = []
        for message in proof.get("messages", [])[:12]:
            text = str(message.get("text") or "").strip()
            if text:
                snippet_parts.append(text[:500])
        if not snippet_parts:
            for link in proof.get("conversation_links", [])[:12]:
                snippet_parts.append(f"{link.get('title', 'conversation')} — {link.get('href', '')}")
        snippet = "\n\n".join(snippet_parts)[:4000]
        staged = multi_ai_conversation_inventory_service.stage_conversation(
            provider=provider,
            title=title,
            snippet=snippet,
            conversation_url=proof.get("final_url") or proof.get("target_url"),
            project_hint=project_hint,
            tenant_id=tenant_id,
            source_status="pc_provider_proof_import",
        )
        return {
            "ok": True,
            "mode": "pc_provider_conversation_proof_import",
            "proof_file": str(path),
            "proof_summary": {
                "provider": provider,
                "message_count": proof.get("message_count", 0),
                "conversation_link_count": proof.get("conversation_link_count", 0),
                "can_read_visible_messages": proof.get("summary", {}).get("can_read_visible_messages"),
            },
            "staged": staged,
        }

    def first_pc_proof_package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "install_plan": self.install_plan(),
            "proofs": self.list_proofs(limit=10),
            "next_commands": [self.provider_proof_command(provider=provider, wait_login_seconds=90) for provider in SUPPORTED_PROVIDERS],
            "proof_goal": {
                "minimum_success": "open provider + confirm ready marker OR import at least one staged conversation manually",
                "strong_success": "open provider + manual login + visible messages read + proof imported to inventory",
                "not_required_for_tomorrow_morning": "automatic sending/deleting/cleanup of provider chats",
            },
        }

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"ok": False, "status": "invalid_json", "error": exc.__class__.__name__, "file": str(path)}


pc_provider_conversation_proof_service = PcProviderConversationProofService()
