from typing import Dict, Any, List
import httpx

GITHUB_API = "https://api.github.com"

class GitHubLazyTreeProvider:
    """
    Lazy tree provider (depth-controlled) for GitHub repos.
    Depth default = 2 (architectural decision)
    Full structure visible progressively.
    """

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    async def fetch_tree(self, repo_full_name: str, depth: int = 2) -> Dict[str, Any]:
        owner, repo = repo_full_name.split("/")

        async with httpx.AsyncClient(timeout=30) as client:
            # get default branch
            repo_resp = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}",
                headers=self.headers
            )
            repo_resp.raise_for_status()
            default_branch = repo_resp.json()["default_branch"]

            # get tree sha
            ref_resp = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/git/ref/heads/{default_branch}",
                headers=self.headers
            )
            ref_resp.raise_for_status()
            tree_sha = ref_resp.json()["object"]["sha"]

            return await self._fetch_tree_recursive(
                client,
                owner,
                repo,
                tree_sha,
                current_depth=0,
                max_depth=depth
            )

    async def _fetch_tree_recursive(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        tree_sha: str,
        current_depth: int,
        max_depth: int
    ) -> Dict[str, Any]:

        tree_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{tree_sha}",
            headers=self.headers
        )
        tree_resp.raise_for_status()
        tree_data = tree_resp.json()

        node = {
            "type": "dir",
            "sha": tree_sha,
            "children": []
        }

        if current_depth >= max_depth:
            return node

        for item in tree_data.get("tree", []):
            if item["type"] == "tree":
                child = await self._fetch_tree_recursive(
                    client,
                    owner,
                    repo,
                    item["sha"],
                    current_depth + 1,
                    max_depth
                )
                child["name"] = item["path"]
                node["children"].append(child)
            else:
                node["children"].append({
                    "type": "file",
                    "name": item["path"],
                    "sha": item["sha"]
                })

        return node
