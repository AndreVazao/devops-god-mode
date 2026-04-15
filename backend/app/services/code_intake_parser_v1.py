import re
from typing import Any


class CodeIntakeParserV1:
    CODE_BLOCK_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
    FILE_HINT_RE = re.compile(r"(?:file|ficheiro|arquivo|path|caminho)\s*[:=-]?\s*([\w./\\-]+)", re.IGNORECASE)
    REPO_HINT_RE = re.compile(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")

    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = (payload.get("text") or "").strip()
        repo_full_name = payload.get("repo_full_name")
        preferred_path = payload.get("preferred_path")

        code_blocks = []
        for match in self.CODE_BLOCK_RE.finditer(text):
            language = (match.group(1) or "").strip().lower() or "unknown"
            content = match.group(2).strip("\n")
            code_blocks.append(
                {
                    "language": language,
                    "content": content,
                    "line_count": len(content.splitlines()) if content else 0,
                }
            )

        repo_match = None if repo_full_name else self.REPO_HINT_RE.search(text)
        resolved_repo = repo_full_name or (repo_match.group(1) if repo_match else None)

        file_hints = []
        if preferred_path:
            file_hints.append(preferred_path)
        file_hints.extend(self.FILE_HINT_RE.findall(text))
        file_hints = [hint.replace('\\', '/').strip() for hint in file_hints if hint.strip()]

        primary_operation = self._infer_operation(text, code_blocks, file_hints)
        target_path = self._infer_target_path(file_hints, code_blocks)
        target_repo_action = "existing_repo" if resolved_repo else "repo_resolution_required"

        return {
            "ok": True,
            "mode": "code_intake",
            "resolved_repo": resolved_repo,
            "target_repo_action": target_repo_action,
            "target_path": target_path,
            "primary_operation": primary_operation,
            "code_block_count": len(code_blocks),
            "code_blocks": code_blocks,
            "file_hints": file_hints,
            "summary": {
                "has_code": len(code_blocks) > 0,
                "has_repo_hint": bool(resolved_repo),
                "has_path_hint": bool(target_path),
            },
        }

    def _infer_operation(self, text: str, code_blocks: list[dict[str, Any]], file_hints: list[str]) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["substitui", "replace", "overwrite", "troca tudo"]):
            return "replace_file"
        if any(word in lowered for word in ["adiciona", "append", "acrescenta", "junta"]):
            return "append_to_file"
        if file_hints and code_blocks:
            return "patch_existing_file"
        if code_blocks:
            return "new_file"
        return "analysis_only"

    def _infer_target_path(self, file_hints: list[str], code_blocks: list[dict[str, Any]]) -> str | None:
        if file_hints:
            return file_hints[0]
        if len(code_blocks) == 1:
            language = code_blocks[0].get("language")
            default_map = {
                "python": "app/main.py",
                "javascript": "src/index.js",
                "typescript": "src/index.ts",
                "tsx": "src/App.tsx",
                "jsx": "src/App.jsx",
                "json": "config/generated.json",
                "yaml": ".github/workflows/generated.yml",
            }
            return default_map.get(language)
        return None


code_intake_parser_v1 = CodeIntakeParserV1()
