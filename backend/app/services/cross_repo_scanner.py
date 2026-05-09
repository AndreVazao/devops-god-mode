import os

REPOS_PATH = "./repos"

def scan_repos(repos_path: str = REPOS_PATH):
    patterns = []

    if not os.path.exists(repos_path):
        return patterns

    for root, dirs, files in os.walk(repos_path):
        for f in files:
            if f.endswith(".py") or f.endswith(".js"):
                path = os.path.join(root, f)

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()

                        if "requests.get" in content:
                            patterns.append({
                                "type": "http_call",
                                "file": path
                            })

                        if "subprocess" in content:
                            patterns.append({
                                "type": "executor_pattern",
                                "file": path
                            })
                except Exception:
                    pass

    return patterns
