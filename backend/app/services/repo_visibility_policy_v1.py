from typing import Any


class RepoVisibilityPolicyV1:
    def plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        desired_visibility = (payload.get("desired_visibility") or "private").lower()
        lifecycle_mode = (payload.get("lifecycle_mode") or "private_only").lower()
        build_strategy = (payload.get("build_strategy") or "standard").lower()
        repo_full_name = payload.get("repo_full_name")
        product_ready = bool(payload.get("product_ready"))

        if desired_visibility not in {"public", "private"}:
            desired_visibility = "private"

        visibility_now = desired_visibility
        visibility_when_ready = desired_visibility
        reason = "Política simples de visibilidade aplicada."
        transitions: list[dict[str, Any]] = []

        if lifecycle_mode == "public_until_product_ready":
            visibility_now = "public"
            visibility_when_ready = "private"
            reason = "Repo pode ficar pública enquanto o produto ainda está em evolução, ficando privada quando estiver pronta/finalizada."
            transitions = [
                {"phase": "development", "visibility": "public", "required": True},
                {"phase": "product_ready", "visibility": "private", "required": True},
            ]
        elif lifecycle_mode == "private_only":
            visibility_now = "private"
            visibility_when_ready = "private"
            reason = "Repo permanece privada durante todo o ciclo."
            transitions = [
                {"phase": "development", "visibility": "private", "required": True},
            ]
        elif lifecycle_mode == "public_only":
            visibility_now = "public"
            visibility_when_ready = "public"
            reason = "Repo permanece pública durante todo o ciclo."
            transitions = [
                {"phase": "development", "visibility": "public", "required": True},
            ]

        current_recommendation = visibility_when_ready if product_ready else visibility_now
        if build_strategy == "github_actions_free_public":
            reason += " Estratégia de build favorece visibilidade pública durante a fase de desenvolvimento."

        return {
            "ok": True,
            "mode": "repo_visibility_policy",
            "repo_full_name": repo_full_name,
            "desired_visibility": desired_visibility,
            "lifecycle_mode": lifecycle_mode,
            "build_strategy": build_strategy,
            "product_ready": product_ready,
            "visibility_now": visibility_now,
            "visibility_when_ready": visibility_when_ready,
            "current_recommendation": current_recommendation,
            "reason": reason,
            "transitions": transitions,
            "approval_required": True,
        }


repo_visibility_policy_v1 = RepoVisibilityPolicyV1()
