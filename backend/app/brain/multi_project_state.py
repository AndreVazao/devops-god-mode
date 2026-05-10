import os
from app.utils.atomic_json_store import AtomicJsonStore
from typing import Dict, Any

FILE = os.path.join("backend", "data", "projects.json")

DEFAULT_DATA = {}

store = AtomicJsonStore(FILE, default_factory=lambda: DEFAULT_DATA)

def load() -> Dict[str, Any]:
    return store.load()

def save(data: Dict[str, Any]):
    store.save(data)

def register_project(name: str, repo_path: str):
    data = load()
    data[name] = {
        "repo": os.path.abspath(repo_path),
        "status": "active",
        "tasks": []
    }
    save(data)

def get_repo_path(name: str) -> str:
    data = load()
    project = data.get(name)
    if project:
        return project.get("repo")
    return os.getcwd()

def ensure_default_project():
    data = load()
    if not data:
        from app.config import settings
        register_project("default", settings.REPOS_PATH)
