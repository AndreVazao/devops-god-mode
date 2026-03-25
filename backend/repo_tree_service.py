class RepoTreeService:
    def generate_tree_preview(self, repo_full_name: str):
        return {"tree_text": repo_full_name}

repo_tree_service = RepoTreeService()
