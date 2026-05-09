import time
import threading
from app.config import settings
from app.services.semantic_index_builder import build_index

def start_semantic_cron(repo_path=None, interval=3600):
    if repo_path is None:
        repo_path = settings.REPOS_PATH
    def run():
        while True:
            try:
                print(f"[SEMANTIC CRON] Rebuilding semantic index for {repo_path}...")
                res = build_index(repo_path)
                print(f"[SEMANTIC CRON] Index rebuilt: {res}")
            except Exception as e:
                print(f"[SEMANTIC CRON] Error rebuilding index: {e}")
            time.sleep(interval)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
