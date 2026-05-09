import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

def execute_code(code: str) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        f.write(code)
        path = f.name

    try:
        # Use sys.executable for better portability (e.g. windows vs linux)
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
