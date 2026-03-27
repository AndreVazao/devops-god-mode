from app.config import settings
from app.services.repo_tree.github_lazy_provider import GitHubLazyTreeProvider
from app.services.repo_tree_analysis_v1 import repo_tree_analysis_v1
from app.services.repo_tree_cache_v2 import repo_tree_cache_v2


class RepoTreeEngineV3:
    def status(self):
        return {
            "ok": True,
            "engine": "repo-tree",
            "provider": "github-lazy",
            "default_depth": 2,
            "store_on_first_read": True,
            "analysis_mode": "progressive",
            "cache_backend": "supabase",
            "analysis_layer": "framework-repo-type-risk-v1",
        }

    async def preview(self, repo_full_name: str, depth: int = 2):
        provider = GitHubLazyTreeProvider(settings.GITHUB_TOKEN)
        tree_json = await provider.fetch_tree(repo_full_name, depth=depth)
        tree_json["name"] = repo_full_name
        tree_json["path"] = repo_full_name
        tree_text = self._render_tree_text(tree_json)
        analysis = repo_tree_analysis_v1.analyze(tree_json)
        cache_result = await repo_tree_cache_v2.save_snapshot(
            repo_full_name=repo_full_name,
            tree_json=tree_json,
            tree_text=tree_text,
            depth=depth,
            analysis_status="partial",
        )
        return {
            "ok": True,
            "repo_full_name": repo_full_name,
            "depth": depth,
            "analysis_status": "partial",
            "cache": cache_result,
            "analysis": analysis,
            "tree_json": tree_json,
            "tree_text": tree_text,
        }

    def _render_tree_text(self, node, prefix: str = "", is_last: bool = True):
        name = node.get("name", "root")
        line = name if prefix == "" else f"{prefix}{'└── ' if is_last else '├── '}{name}"
        children = node.get("children", [])
        if not children:
            return line
        child_prefix = prefix + ("    " if is_last else "│   ")
        rendered = [line]
        for index, child in enumerate(children):
            child_is_last = index == len(children) - 1
            rendered.append(self._render_tree_text(child, child_prefix, child_is_last))
        return "\n".join(rendered)


repo_tree_engine_v3 = RepoTreeEngineV3()
