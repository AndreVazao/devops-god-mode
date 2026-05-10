from app.services.ai_fix_service import generate_fix, apply_fix

def fix_errors(validation_result):
    """
    Attempts to fix errors automatically using AI fix service.
    """
    print("🛠 Attempting auto-fix...")

    logs = validation_result.get("log", "")
    fix = generate_fix(logs)

    if not fix or fix.get("type") == "noop":
        print("⚠️ No fix generated.")
        return False

    print(f"Applying fix: {fix.get('description')}")
    apply_fix(fix)
    return True
