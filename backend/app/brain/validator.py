from typing import Any

def validate(result: Any):
    """
    Validates the result of an execution.
    For now, provides a simple pass-through validation.
    """
    print(f"🔍 [Validator] Validating result...")

    # Heuristic for failure in result
    if isinstance(result, dict) and result.get("status") == "failed":
        return {"ok": False, "message": "Validation failed: status is failed"}

    if "error" in str(result).lower():
         return {"ok": False, "message": f"Validation failed: error detected in result: {result}"}

    return {"ok": True, "message": "Validation passed."}
