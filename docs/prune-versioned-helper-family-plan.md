# Prune Versioned Helper Family Plan

## Branch
- `feature/big-v1-helper-prune`

## Objective
Remove a full batch of old versioned helper services that no longer participate in the active runtime path of the God Mode backend.

## Scope
- `backend/app/services/approval_shell_v1.py`
- `backend/app/services/browser_prompt_builder_v1.py`
- `backend/app/services/code_intake_parser_v1.py`
- `backend/app/services/code_intake_pipeline_v1.py`
- `backend/app/services/git_ops_plan_v1.py`
- `backend/app/services/mobile_cockpit_payload_v1.py`
- `backend/app/services/ops_execution_pipeline_v1.py`
- `backend/app/services/pr_execution_plan_v1.py`
- `backend/app/services/repo_resolution_engine_v1.py`
- `backend/app/services/repo_visibility_policy_v1.py`
- `backend/app/services/workflow_error_intake_v1.py`
- `backend/app/services/workflow_repair_prompt_v1.py`
- remove merged repo tree internals cleanup scaffolding files

## Expected Result
- noticeably smaller `backend/app/services/` surface
- less versioned helper noise around the active service layer
- cleaner next pass for identifying any remaining dead helper families
