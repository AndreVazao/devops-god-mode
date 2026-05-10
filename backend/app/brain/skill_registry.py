from __future__ import annotations
from typing import Dict, Optional

SKILLS: Dict[str, str] = {
    "deploy_vercel": "scripts/deploy_vercel.py",
    "fix_tests": "scripts/fix_tests.py",
    "scan_errors": "scripts/scan_errors.py"
}

def get_skill(name: str) -> Optional[str]:
    """
    Retrieves the script path associated with a skill name.
    """
    return SKILLS.get(name)
