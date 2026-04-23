from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class CapabilityReuseService:
    def __init__(self) -> None:
        self.search_roots = [
            Path("data/conversation_repo_materializations"),
            Path("data/staged_asset_workspace"),
            Path("backend"),
            Path("desktop"),
        ]
        self.capability_patterns = {
            "ocr": ["ocr", "tesseract", "easyocr", "pytesseract", "image_to_string"],
            "adb": ["adb", "uiautomator", "android", "shell input tap"],
            "fastapi": ["fastapi", "apirouter", "uvicorn"],
            "nextjs": ["next", "page.tsx", "app router", "react"],
            "websocket": ["websocket", "ws://", "websockets", "socket"],
            "opencv": ["opencv", "cv2", "matchtemplate", "imread"],
            "sqlite": ["sqlite", "sqlite3", "database"],
        }

    def _iter_candidate_files(self) -> List[Path]:
        files: List[Path] = []
        for root in self.search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".json", ".md", ".txt"}:
                    files.append(path)
        return files

    def _match_score(self, text: str, patterns: List[str]) -> int:
        lowered = text.lower()
        return sum(1 for pattern in patterns if pattern.lower() in lowered)

    def lookup_capability(self, capability_name: str) -> Dict[str, Any]:
        patterns = self.capability_patterns.get(capability_name.lower(), [capability_name])
        matches: List[Dict[str, Any]] = []
        for path in self._iter_candidate_files():
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            score = self._match_score(content, patterns) + self._match_score(str(path), patterns)
            if score <= 0:
                continue
            preview_lines = []
            for line in content.splitlines():
                if any(pattern.lower() in line.lower() for pattern in patterns):
                    preview_lines.append(line.strip())
                if len(preview_lines) >= 3:
                    break
            matches.append(
                {
                    "file_path": str(path),
                    "score": score,
                    "preview": "\n".join(preview_lines),
                }
            )
        matches.sort(key=lambda item: (item["score"], item["file_path"]), reverse=True)
        return {
            "ok": True,
            "mode": "capability_reuse_lookup_result",
            "capability_name": capability_name,
            "match_count": len(matches),
            "matches": matches[:20],
        }

    def suggest_reuse_plan(self, capability_name: str, target_project: str) -> Dict[str, Any]:
        lookup = self.lookup_capability(capability_name)
        top_matches = lookup.get("matches", [])[:5]
        plan_items = []
        for item in top_matches:
            plan_items.append(
                {
                    "source_file": item["file_path"],
                    "target_project": target_project,
                    "adaptation_action": "review_and_adapt_existing_capability",
                    "score": item["score"],
                }
            )
        return {
            "ok": True,
            "mode": "capability_reuse_plan_result",
            "capability_name": capability_name,
            "target_project": target_project,
            "reuse_candidate_count": len(plan_items),
            "plan_items": plan_items,
        }

    def export_capability_index(self) -> Dict[str, Any]:
        index = {}
        for capability_name in sorted(self.capability_patterns.keys()):
            lookup = self.lookup_capability(capability_name)
            index[capability_name] = lookup.get("matches", [])[:10]
        output_path = Path("data/capability_reuse_index.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "capability_reuse_index_result",
            "output_file": str(output_path),
            "capability_count": len(index),
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "capability_reuse_status",
            "search_roots": [str(item) for item in self.search_roots],
            "capability_count": len(self.capability_patterns),
            "status": "capability_reuse_ready",
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "capability_reuse_package",
            "package": {
                "status": self.get_status(),
                "package_status": "capability_reuse_ready",
            },
        }


capability_reuse_service = CapabilityReuseService()
