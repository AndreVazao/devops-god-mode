from app.services.local_executor_service import execute_code

def run_step(step: str):
    """
    Executes a single step using the LocalExecutorService.
    If the step looks like code, it executes it.
    Otherwise, it treats it as a descriptive step and logs execution.
    """
    print(f"🤖 [Agent Pool] Running step: {step}")

    # Explicit code detection: multiple lines, assignment, or common keywords
    code_indicators = ["def ", "import ", "print(", " = ", "from ", "if ", "for ", "while "]
    is_code = "\n" in step or any(indicator in step for indicator in code_indicators)

    if is_code:
        print(f"💻 [Agent Pool] Detected code execution for: {step[:50]}...")
        result = execute_code(step)
        return {
            "status": "completed" if result.get("returncode") == 0 else "failed",
            "result": result.get("stdout") or result.get("stderr") or result.get("error")
        }

    # Descriptive step - just acknowledge
    return {
        "status": "acknowledged",
        "result": f"Step '{step}' acknowledged by Agent Pool."
    }
