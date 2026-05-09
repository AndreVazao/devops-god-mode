import os
import subprocess

MAX_FILES_CHANGED = 20
FORBIDDEN_PATTERNS = [".github/workflows", "secrets", "env"]

def generate_fix(ci_logs: str):
    if not ci_logs:
        return None

    # Heurística simples (integrar com LLM futuramente)
    if "ModuleNotFoundError" in ci_logs:
        return {
            "type": "edit_file",
            "file": "backend/requirements.txt",
            "content_append": "\n# missing-module-placeholder"
        }

    if "SyntaxError" in ci_logs:
        return {
            "type": "noop"
        }

    return None

def is_safe_to_apply(fix: dict):
    if not fix:
        return True

    if fix["type"] == "edit_file":
        filepath = fix["file"]
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in filepath:
                print(f"[SAFETY] Forbidden file pattern detected: {filepath}")
                return False

    # Check total files changed
    try:
        res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
        files_changed = res.stdout.strip().split("\n")
        if len(files_changed) >= MAX_FILES_CHANGED:
            print(f"[SAFETY] Too many files changed: {len(files_changed)}")
            return False
    except Exception:
        pass

    return True

def apply_fix(fix: dict):
    if not fix:
        return

    if not is_safe_to_apply(fix):
        print("[SAFETY] Fix rejected by safety guard.")
        return

    if fix["type"] == "edit_file":
        filepath = fix["file"]
        if os.path.exists(filepath):
            with open(filepath, "a") as f:
                f.write(fix["content_append"])
        else:
             # Create new file if it doesn't exist
             os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
             with open(filepath, "w") as f:
                f.write(fix["content_append"])
