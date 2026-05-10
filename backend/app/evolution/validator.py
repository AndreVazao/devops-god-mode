import subprocess

def validate_changes(execution_result):
    """
    Validates changes by running tests.
    Can also check the execution_result status.
    """
    print("🔍 Running system validation (pytest)...")

    # Check if execution result reported success first
    if execution_result.get("status") not in ["completed", "git_done", "done"]:
        return {
            "success": False,
            "log": f"Execution failed with status: {execution_result.get('status')}. Error: {execution_result.get('error')}"
        }

    # Run actual tests
    try:
        r = subprocess.run(["pytest", "backend/app/evolution"], capture_output=True, timeout=60)
        return {
            "success": r.returncode == 0,
            "log": r.stdout.decode() + "\n" + r.stderr.decode()
        }
    except Exception as e:
        return {
            "success": False,
            "log": f"Validation error: {str(e)}"
        }
