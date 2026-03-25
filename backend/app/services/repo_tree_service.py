class RepoTreeService:
    def status(self):
        return {"ok": True, "engine": "repo-tree", "mode": "bootstrap"}

repo_tree_service = RepoTreeService()
