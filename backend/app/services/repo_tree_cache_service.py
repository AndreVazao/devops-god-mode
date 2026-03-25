class RepoTreeCacheService:
    def status(self):
        return {"ok": True, "cache": "planned", "strategy": "store-on-first-read"}

repo_tree_cache_service = RepoTreeCacheService()
