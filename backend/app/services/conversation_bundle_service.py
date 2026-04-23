from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.browser_conversation_intake_service import browser_conversation_intake_service


class ConversationBundleService:
    def __init__(self, storage_path: str = "data/conversation_bundle_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"bundles": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"bundles": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _slugify(self, value: str, fallback: str = "project") -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
        return normalized or fallback

    def _infer_provider(self, source_url: str, source_type: str) -> str:
        lowered = f"{source_type} {source_url}".lower()
        if "chatgpt" in lowered or "openai" in lowered:
            return "chatgpt"
        if "claude" in lowered or "anthropic" in lowered:
            return "claude"
        if "gemini" in lowered or "google" in lowered:
            return "gemini"
        if "grok" in lowered or "x.ai" in lowered:
            return "grok"
        if "deepseek" in lowered:
            return "deepseek"
        return "unknown"

    def _normalize_code_block(self, block: Dict[str, Any], provider: str, session_id: str) -> Dict[str, Any]:
        code = str(block.get("code") or block.get("content") or "")
        language = str(block.get("language") or block.get("lang") or "text")
        path_hint = str(block.get("path") or block.get("file_path") or "")
        return {
            "language": language,
            "path_hint": path_hint,
            "code": code,
            "line_count": len(code.splitlines()) if code else 0,
            "has_code": bool(code.strip()),
            "provider": provider,
            "session_id": session_id,
        }

    def _extract_repo_targets(self, code_blocks: List[Dict[str, Any]]) -> List[str]:
        targets: List[str] = []
        for block in code_blocks:
            path_hint = str(block.get("path_hint") or "").strip()
            if path_hint:
                targets.append(path_hint)
        return sorted(list(dict.fromkeys(targets)))

    def _bundle_summary(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "bundle_id": bundle["bundle_id"],
            "bundle_name": bundle["bundle_name"],
            "project_key": bundle["project_key"],
            "provider_count": len(bundle.get("providers", [])),
            "session_count": len(bundle.get("sessions", [])),
            "code_block_count": len(bundle.get("normalized_code_blocks", [])),
            "repo_targets": bundle.get("repo_targets", []),
            "status": bundle.get("status"),
            "updated_at": bundle.get("updated_at"),
        }

    def create_bundle_from_sessions(
        self,
        session_ids: List[str],
        project_hint: Optional[str] = None,
        bundle_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = []
        for session_id in session_ids:
            session = browser_conversation_intake_service.get_session(session_id)
            if not session:
                return {
                    "ok": False,
                    "mode": "conversation_bundle_create_result",
                    "bundle_status": "session_not_found",
                    "session_id": session_id,
                }
            sessions.append(session)

        providers = sorted(
            list(
                {
                    self._infer_provider(
                        source_url=str(session.get("source_url") or ""),
                        source_type=str(session.get("source_type") or ""),
                    )
                    for session in sessions
                }
            )
        )
        normalized_code_blocks: List[Dict[str, Any]] = []
        snippets: List[Dict[str, Any]] = []
        warnings: List[str] = []
        titles: List[str] = []
        for session in sessions:
            provider = self._infer_provider(
                source_url=str(session.get("source_url") or ""),
                source_type=str(session.get("source_type") or ""),
            )
            titles.append(str(session.get("conversation_title") or ""))
            warnings.extend([str(item) for item in session.get("warnings", [])])
            snippets.extend(session.get("snippets", []))
            normalized_code_blocks.extend(
                [
                    self._normalize_code_block(block, provider=provider, session_id=session["session_id"])
                    for block in session.get("code_blocks", [])
                ]
            )

        project_key = self._slugify(project_hint or titles[0] if titles else "project")
        bundle_id = f"bundle_{uuid.uuid4().hex[:12]}"
        final_bundle_name = bundle_name or f"{project_key}-multi-provider"
        repo_targets = self._extract_repo_targets(normalized_code_blocks)
        bundle = {
            "bundle_id": bundle_id,
            "bundle_name": final_bundle_name,
            "project_key": project_key,
            "providers": providers,
            "sessions": [
                {
                    "session_id": session["session_id"],
                    "source_url": session.get("source_url"),
                    "source_type": session.get("source_type"),
                    "conversation_title": session.get("conversation_title"),
                    "capture_status": session.get("capture_status"),
                    "provider": self._infer_provider(
                        source_url=str(session.get("source_url") or ""),
                        source_type=str(session.get("source_type") or ""),
                    ),
                }
                for session in sessions
            ],
            "normalized_code_blocks": normalized_code_blocks,
            "snippets": snippets,
            "warnings": sorted(list(dict.fromkeys([item for item in warnings if item]))),
            "repo_targets": repo_targets,
            "status": "bundle_created",
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("bundles", []).append(bundle)
            self._write_store(store)
        return {
            "ok": True,
            "mode": "conversation_bundle_create_result",
            "bundle_status": "bundle_created",
            "bundle": bundle,
        }

    def list_bundles(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        bundles = [self._bundle_summary(item) for item in store.get("bundles", [])]
        return {
            "ok": True,
            "mode": "conversation_bundle_list",
            "count": len(bundles),
            "bundles": bundles,
        }

    def get_bundle(self, bundle_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for bundle in store.get("bundles", []):
            if bundle.get("bundle_id") == bundle_id:
                return bundle
        return None

    def auto_group_captured_sessions(self) -> Dict[str, Any]:
        sessions = browser_conversation_intake_service.list_sessions().get("sessions", [])
        grouped: Dict[str, List[str]] = {}
        for session in sessions:
            if session.get("code_blocks_count", 0) <= 0:
                continue
            key = self._slugify(str(session.get("project_hint") or session.get("conversation_title") or "project"))
            grouped.setdefault(key, []).append(session["session_id"])
        created: List[Dict[str, Any]] = []
        for project_key, session_ids in grouped.items():
            if not session_ids:
                continue
            created.append(
                self.create_bundle_from_sessions(
                    session_ids=session_ids,
                    project_hint=project_key,
                    bundle_name=f"{project_key}-grouped",
                )
            )
        return {
            "ok": True,
            "mode": "conversation_bundle_auto_group_result",
            "group_count": len(grouped),
            "created_count": len(created),
            "results": created,
        }

    def build_repo_materialization_plan(self, bundle_id: str, repository_name: Optional[str] = None) -> Dict[str, Any]:
        bundle = self.get_bundle(bundle_id)
        if not bundle:
            return {
                "ok": False,
                "mode": "conversation_bundle_repo_plan",
                "plan_status": "bundle_not_found",
                "bundle_id": bundle_id,
            }
        repo_name = repository_name or bundle["project_key"]
        file_plan: List[Dict[str, Any]] = []
        unnamed_counter = 1
        for block in bundle.get("normalized_code_blocks", []):
            destination = block.get("path_hint") or f"generated/snippet_{unnamed_counter}.{block.get('language') or 'txt'}"
            unnamed_counter += 1
            file_plan.append(
                {
                    "destination_path": destination,
                    "language": block.get("language"),
                    "line_count": block.get("line_count"),
                    "content_preview": (block.get("code") or "")[:200],
                    "content_full": block.get("code") or "",
                    "provider": block.get("provider") or "unknown",
                    "session_id": block.get("session_id"),
                    "source_kind": "conversation_code_block",
                }
            )
        plan = {
            "bundle_id": bundle_id,
            "repository_name": repo_name,
            "project_key": bundle.get("project_key"),
            "providers": bundle.get("providers", []),
            "file_plan": file_plan,
            "warning_count": len(bundle.get("warnings", [])),
            "repo_target_count": len(bundle.get("repo_targets", [])),
            "plan_status": "repo_plan_ready",
        }
        return {
            "ok": True,
            "mode": "conversation_bundle_repo_plan",
            "plan_status": "repo_plan_ready",
            "plan": plan,
        }

    def get_status(self) -> Dict[str, Any]:
        bundle_list = self.list_bundles()
        session_queue = browser_conversation_intake_service.list_sessions()
        return {
            "ok": True,
            "mode": "conversation_bundle_status",
            "bundle_count": bundle_list["count"],
            "session_count": session_queue["count"],
            "storage": str(self.storage_path),
            "status": "conversation_bundle_ready",
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "conversation_bundle_package",
            "package": {
                "status": self.get_status(),
                "sessions": browser_conversation_intake_service.list_sessions(),
                "bundles": self.list_bundles(),
                "package_status": "conversation_bundle_ready",
            },
        }


conversation_bundle_service = ConversationBundleService()
