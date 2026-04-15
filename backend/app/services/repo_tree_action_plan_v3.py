from app.config import settings
from app.services.repo_tree.github_lazy_provider import GitHubLazyTreeProvider
from app.services.repo_tree_action_plan_v2 import repo_tree_action_plan_v2
from app.services.repo_tree_analysis_v2 import repo_tree_analysis_v2


class RepoTreeActionPlanV3:
    async def build_live(self, repo_full_name: str, depth: int = 2):
        provider = GitHubLazyTreeProvider(settings.GITHUB_TOKEN)
        tree_json = await provider.fetch_tree(repo_full_name, depth=depth)
        tree_json["name"] = repo_full_name
        tree_json["path"] = repo_full_name
        analysis = repo_tree_analysis_v2.analyze(tree_json)
        embedded_snapshot = {
            "id": None,
            "depth": depth,
            "analysis_status": "live_fallback",
            "structural_hash": None,
            "frameworks": analysis.get("frameworks") or [],
            "repo_types": analysis.get("repo_types") or [],
            "risks": analysis.get("risks") or [],
            "recommendations": analysis.get("recommendations") or [],
        }
        result = repo_tree_action_plan_v2.build_from_embedded_snapshot(repo_full_name, embedded_snapshot)
        result["fallback_used"] = True
        result["fallback_reason"] = "live_provider_without_supabase"
        return result


repo_tree_action_plan_v3 = RepoTreeActionPlanV3()
