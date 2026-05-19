import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.home_system_health_service import home_system_health_service
from app.services.godmode_diagnostics_service import godmode_diagnostics_service
from app.services.first_pc_runtime_verification_service import first_pc_runtime_verification_service
from app.services.god_mode_self_diagnosis_mission_control_service import god_mode_self_diagnosis_mission_control_service
from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service

def run_checkup():
    print("--- GOD MODE INTEGRATED CHECKUP ---")

    # 1. System Health
    print("\n[1/5] Checking Home System Health...")
    health = home_system_health_service.get_status()
    print(f"Status: {health.get('status')}")
    print(f"Health Score: {health.get('health_score')}")

    # 2. Diagnostics
    print("\n[2/5] Running Subsystem Diagnostics...")
    diag = godmode_diagnostics_service.build_dashboard()
    print(f"Blockers found: {diag.get('blocker_count')}")
    for b in diag.get('blockers', []):
        print(f" - {b}")

    # 3. Ready to Use Checklist
    print("\n[3/5] Running 'Ready to Use' Checklist...")
    ready_data = ready_to_use_home_check_service.build_checklist()
    print(f"Readiness Score: {ready_data.get('readiness_score')}%")
    print(f"Failed checks: {ready_data.get('failed_count')}")
    for b in ready_data.get('blockers', []):
        print(f" - [FAIL] {b.get('label')}: {b.get('detail')}")

    # 4. Runtime Verification
    print("\n[4/5] Verifying PC Runtime...")
    verification = first_pc_runtime_verification_service.status()
    print(f"Verification Ready: {verification.get('pc_runtime_verification_ready')}")
    print(f"Essential Routes: {verification.get('essential_route_count')}")

    # 5. Self-Diagnosis (Gaps)
    print("\n[5/5] Running Self-Diagnosis Gap Detection...")
    # Trigger a run
    self_diag_run = god_mode_self_diagnosis_mission_control_service.run_diagnosis()
    print(f"Diagnostic Run ID: {self_diag_run.get('diagnostic_run_id')}")
    gaps = self_diag_run.get('gaps', [])
    print(f"Gaps found: {len(gaps)}")
    for g in gaps:
        print(f" - [{g.get('severity')}] {g.get('gap_id')}: {g.get('reason')}")

    print("\n--- CHECKUP COMPLETE ---")

    summary = {
        "health_ok": health.get("ok"),
        "health_score": health.get("health_score"),
        "blockers": diag.get("blocker_count"),
        "ready_score": ready_data.get("readiness_score"),
        "gaps": len(gaps)
    }
    return summary

if __name__ == "__main__":
    try:
        summary = run_checkup()
        if summary["health_ok"] and summary["blockers"] == 0 and summary["ready_score"] >= 75:
            print("\n✅ System appears stable and operational.")
        else:
            print("\n⚠️ System has issues that may require attention.")
    except Exception as e:
        print(f"\n❌ Checkup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
