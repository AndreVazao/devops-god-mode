from .cross_repo_scanner import scan_repos
from .pattern_library import pattern_library_service
from .architecture_suggester import suggest_architecture

class CrossProjectIntelligenceService:
    def run_cross_intelligence(self, context: list[str]):
        # 1. Scan for patterns
        patterns = scan_repos()

        # 2. Store patterns found
        pattern_library_service.store_patterns(patterns)

        # 3. Generate suggestions based on context
        suggestions = suggest_architecture(context)

        return {
            "patterns_found": len(patterns),
            "patterns_by_type": pattern_library_service.get_all_patterns(),
            "suggestions": suggestions
        }

cross_project_intelligence_service = CrossProjectIntelligenceService()
