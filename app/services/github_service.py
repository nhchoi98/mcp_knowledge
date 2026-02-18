from __future__ import annotations

from typing import Any

from ..config import SETTINGS
from ..github_sync import GitHubSyncError
from ..models.github import CreatePRInput, CreatePROutput, GitHubSyncStateInput, GitHubSyncStateOutput
from .document_service import ToolError, _github


class GitHubService:
    @staticmethod
    def github_connection_probe() -> dict[str, Any]:
        if SETTINGS.backend != "github":
            return {"connected": False, "backend": SETTINGS.backend, "reason": "backend is not github"}

        try:
            manager = _github()
            workspace = manager.workspace_root()
            manager.ensure_repo()
            remote_url = manager._run(["git", "-C", str(workspace), "remote", "get-url", manager.remote_name], cwd=workspace)
            manager._run(
                ["git", "-C", str(workspace), "ls-remote", "--exit-code", manager.remote_name, manager.ref],
                cwd=workspace,
            )
            return {
                "connected": True,
                "backend": SETTINGS.backend,
                "repository": manager.repo,
                "ref": manager.ref,
                "workspace": str(workspace),
                "remote_url": remote_url,
            }
        except GitHubSyncError as exc:
            return {"connected": False, "backend": SETTINGS.backend, "reason": str(exc)}
        except Exception as exc:  # pragma: no cover
            return {"connected": False, "backend": SETTINGS.backend, "reason": str(exc)}

    @staticmethod
    def sync_status(payload: GitHubSyncStateInput) -> GitHubSyncStateOutput:
        if SETTINGS.backend != "github":
            raise ToolError("sync_status is only available when KNOWLEDGE_BACKEND=github", status_code=403)

        state = _github().sync_state()
        return GitHubSyncStateOutput(
            branch=state.branch,
            workspace=str(state.workspace),
            remote_url=state.remote_url,
            staged_files=state.staged_files,
            unstaged_files=state.unstaged_files,
            untracked_files=state.untracked_files,
            has_unpushed_commits=state.has_unpushed_commits,
            is_clean=state.is_clean,
            ready_for_pr=bool(state.staged_files),
            push_command=f"git -C {state.workspace} push origin {state.branch}",
            ready_for_pull=state.is_clean,
        )

    @staticmethod
    def create_pr(payload: CreatePRInput) -> CreatePROutput:
        if SETTINGS.backend != "github":
            raise ToolError("create_pr is only available when KNOWLEDGE_BACKEND=github", status_code=403)

        branch, pr_url = _github().create_pr(
            branch=payload.branch,
            commit_message=payload.commit_message,
            base=payload.base,
        )
        return CreatePROutput(
            ok=True,
            branch=branch,
            commit_message=payload.commit_message,
            pr_url=pr_url,
            push_command=f"git -C {_github().workspace_root()} push origin {branch}",
        )
