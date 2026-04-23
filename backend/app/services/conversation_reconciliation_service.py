from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Any, Dict, List

from app.services.conversation_bundle_service import conversation_bundle_service


class ConversationReconciliationService:
    def __init__(self, storage_path: str = "data/conversation_reconciliation_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({"reports": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _normalize_code(self, code: str) -> str:
        lowered = code.strip().lower()
        lowered = re.sub(r"\s+", " ", lowered)
        return lowered

    def _path_key(self, block: Dict[str, Any], index: int) -> str:
        path_hint = str(block.get("path_hint") or "").strip()
        if path_hint:
            return path_hint
        language = str(block.get("language") or "text")
        return f"generated/unknown_{index}.{language}"

    def reconcile_bundle(self, bundle_id: str) -> Dict[str, Any]:
        bundle = conversation_bundle_service.get_bundle(bundle_id)
        if not bundle:
            return {
                "ok": False,
                "mode": "conversation_reconciliation_result",
                "reconciliation_status": "bundle_not_found",
                "bundle_id": bundle_id,
            }

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for index, block in enumerate(bundle.get("normalized_code_blocks", []), start=1):
            grouped.setdefault(self._path_key(block, index), []).append(block)

        deduplicated_blocks: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        duplicates_removed = 0

        for destination_path, blocks in grouped.items():
            seen_code: Dict[str, Dict[str, Any]] = {}
            unique_blocks: List[Dict[str, Any]] = []
            for block in blocks:
                code_key = self._normalize_code(str(block.get("code") or ""))
                if code_key in seen_code:
                    duplicates_removed += 1
                    continue
                seen_code[code_key] = block
                unique_blocks.append(block)

            if len(unique_blocks) > 1:
                conflicts.append(
                    {
                        "destination_path": destination_path,
                        "candidate_count": len(unique_blocks),
                        "languages": sorted(list({str(item.get('language') or 'text') for item in unique_blocks})),
                        "line_counts": [int(item.get("line_count") or 0) for item in unique_blocks],
                    }
                )

            chosen = sorted(unique_blocks, key=lambda item: int(item.get("line_count") or 0), reverse=True)[0]
            deduplicated_blocks.append(
                {
                    "destination_path": destination_path,
                    "language": chosen.get("language"),
                    "line_count": chosen.get("line_count"),
                    "code": chosen.get("code"),
                    "path_hint": chosen.get("path_hint") or destination_path,
                    "source_status": "conflict_selected" if len(unique_blocks) > 1 else "single_or_deduplicated",
                }
            )

        report = {
            "bundle_id": bundle_id,
            "bundle_name": bundle.get("bundle_name"),
            "project_key": bundle.get("project_key"),
            "provider_count": len(bundle.get("providers", [])),
            "original_code_block_count": len(bundle.get("normalized_code_blocks", [])),
            "deduplicated_code_block_count": len(deduplicated_blocks),
            "duplicates_removed": duplicates_removed,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "deduplicated_blocks": deduplicated_blocks,
            "reconciliation_status": "reconciled",
        }

        with self._lock:
            store = self._read_store()
            reports = [item for item in store.get("reports", []) if item.get("bundle_id") != bundle_id]
            reports.append(report)
            store["reports"] = reports
            self._write_store(store)

        return {
            "ok": True,
            "mode": "conversation_reconciliation_result",
            "reconciliation_status": "reconciled",
            "report": report,
        }

    def get_report(self, bundle_id: str) -> Dict[str, Any]:
        store = self._read_store()
        for report in store.get("reports", []):
            if report.get("bundle_id") == bundle_id:
                return {"ok": True, "mode": "conversation_reconciliation_report", "report": report}
        return {"ok": False, "mode": "conversation_reconciliation_report", "report_status": "not_found", "bundle_id": bundle_id}

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "conversation_reconciliation_status",
            "report_count": len(store.get("reports", [])),
            "storage": str(self.storage_path),
            "status": "conversation_reconciliation_ready",
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "conversation_reconciliation_package",
            "package": {
                "status": self.get_status(),
                "bundles": conversation_bundle_service.list_bundles(),
                "package_status": "conversation_reconciliation_ready",
            },
        }


conversation_reconciliation_service = ConversationReconciliationService()
