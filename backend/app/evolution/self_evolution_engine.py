import time
import threading
from .memory_reader import read_memory
from .planner import generate_plan
from .executor import execute_plan
from .validator import validate_changes
from .fixer import fix_errors
from .approval import requires_approval, wait_for_approval

LOOP_INTERVAL = 60  # Check every 60 seconds

def run_evolution_cycle():
    """Performs a single cycle of the self-evolution loop."""
    print("🧠 Starting Self-Evolution Cycle...")

    try:
        # 1. Read Memory
        memory = read_memory()

        # 2. Plan Evolution
        plan = generate_plan(memory)

        if not plan:
            print("😴 No evolution needed at this time.")
            return

        print(f"📋 New Plan Generated: {plan['title']}")

        # 3. Approval Gate
        if requires_approval(plan):
            print("⛔ Plan requires approval. Waiting for mobile cockpit...")
            approved = wait_for_approval(plan)
            if not approved:
                print("🛑 Evolution plan was rejected.")
                return
            print("✅ Evolution plan approved. Proceeding to execution.")

        # 4. Execute Plan
        execution_result = execute_plan(plan)

        # 5. Validate Changes
        validation = validate_changes(execution_result)

        # 6. Auto-Fix if needed
        if not validation["success"]:
            print(f"❌ Validation failed: {validation.get('log')[:200]}...")
            fixed = fix_errors(validation)
            if fixed:
                 print("🛠 Fix applied. Re-validating...")
                 # One re-validation attempt
                 validation = validate_changes(execution_result)
                 if validation["success"]:
                     print("✅ Re-validation successful after fix.")
                 else:
                     print("💀 Validation failed even after fix.")
            else:
                print("⚠️ Auto-fix was not possible.")
        else:
            print("✅ Evolution changes validated successfully.")

        print("✨ Self-Evolution Cycle Completed.")

    except Exception as e:
        print(f"🔥 Error during evolution cycle: {str(e)}")

def start_evolution_engine():
    """Starts the self-evolution engine in a background thread."""
    def loop():
        print("🧠 God Mode Self-Evolution Engine Active")
        while True:
            run_evolution_cycle()
            time.sleep(LOOP_INTERVAL)

    thread = threading.Thread(target=loop, daemon=True, name="SelfEvolutionEngine")
    thread.start()
    return thread
