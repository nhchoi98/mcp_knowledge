from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from .config import SETTINGS


class GitHubSyncError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class GitHubSyncState:
    branch: str
    workspace: Path
    remote_url: str
    staged_files: list[str]
    unstaged_files: list[str]
    untracked_files: list[str]
    has_unpushed_commits: bool

    @property
    def is_clean(self) -> bool:
        return not self.staged_files and not self.unstaged_files and not self.untracked_files


class GitHubSyncManager:
    _branch_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
    _invalid_branch_pattern = re.compile(r"(\.\.)|(@\{)|[\\\s\^:\*\[\]\?]|~")
    _min_branch_len = 1
    _max_branch_len = 100

    def __init__(self) -> None:
        if SETTINGS.backend != "github":
            raise GitHubSyncError("GitHub sync requires KNOWLEDGE_BACKEND=github", status_code=500)
        if not SETTINGS.github_repo:
            raise GitHubSyncError("GITHUB_REPO is required when KNOWLEDGE_BACKEND=github", status_code=500)

        self.repo = SETTINGS.github_repo
        self.ref = SETTINGS.github_ref
        self.token = SETTINGS.github_token
        self.timeout = SETTINGS.github_timeout_seconds
        self.root = SETTINGS.knowledge_root / self._repo_folder_name()
        self.remote_name = "origin"

    def _repo_folder_name(self) -> str:
        safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", self.repo)
        return safe

    def _repo_url(self) -> str:
        if self.token:
            encoded = quote(self.token, safe="")
            return f"https://x-access-token:{encoded}@github.com/{self.repo}.git"
        return f"https://github.com/{self.repo}.git"

    def _validate_branch_name(self, branch: str) -> str:
        safe = branch.strip()
        if not safe:
            raise GitHubSyncError("branch name is required", status_code=422)
        if len(safe) < self._min_branch_len or len(safe) > self._max_branch_len:
            raise GitHubSyncError(
                f"branch length must be between {self._min_branch_len} and {self._max_branch_len}",
                status_code=422,
            )
        if safe != safe.strip("/"):
            raise GitHubSyncError("branch cannot start or end with '/'", status_code=422)
        if not self._branch_pattern.fullmatch(safe):
            raise GitHubSyncError(
                "branch contains invalid characters; allowed: A-Z a-z 0-9 . _ / -",
                status_code=422,
            )
        if self._invalid_branch_pattern.search(safe):
            raise GitHubSyncError(
                "branch contains invalid git ref characters", 
                status_code=422,
            )
        if "//" in safe or ".." in safe:
            raise GitHubSyncError("branch cannot contain '//' or '..'", status_code=422)
        if safe.endswith(".lock"):
            raise GitHubSyncError("branch cannot end with '.lock'", status_code=422)
        for part in safe.split("/"):
            if not part:
                raise GitHubSyncError("branch cannot contain empty path segments", status_code=422)
            if part.startswith(".") or part.endswith("."):
                raise GitHubSyncError("branch components cannot start or end with '.'", status_code=422)
            if part.startswith("-"):
                raise GitHubSyncError("branch components cannot start with '-'", status_code=422)
        return safe

    def _normalize_base_ref(self, base: str) -> str:
        base_ref = base.strip()
        if base_ref.startswith(f"{self.remote_name}/"):
            base_ref = base_ref[len(f"{self.remote_name}/") :]
        return base_ref

    def _parse_repo_owner_name(self) -> tuple[str, str]:
        if "/" not in self.repo:
            raise GitHubSyncError("GITHUB_REPO must be in owner/repo format", status_code=500)
        owner, repo = self.repo.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()
        if not owner or not repo:
            raise GitHubSyncError("GITHUB_REPO must be in owner/repo format", status_code=500)
        return owner, repo

    def _api_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "mcp-knowledge",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _create_pull_request(
        self,
        branch: str,
        base: str,
        title: str,
    ) -> str:
        owner, repo = self._parse_repo_owner_name()
        body = {
            "title": title[:120],
            "head": branch,
            "base": self._normalize_base_ref(base),
            "body": f"Automated PR for knowledge updates on branch `{branch}`.",
        }
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=payload,
            headers=self._api_headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise GitHubSyncError(
                f"GitHub API error while creating PR: HTTP {exc.code}. {raw}".strip(),
                status_code=502,
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubSyncError(f"GitHub API request failed: {exc}", status_code=502) from exc

        try:
            data = json.loads(raw or "{}")
        except Exception as exc:
            raise GitHubSyncError(f"failed to parse GitHub API response: {raw[:200]}", status_code=502) from exc

        pr_url = data.get("html_url")
        if not pr_url:
            raise GitHubSyncError(f"GitHub API response missing html_url: {data}", status_code=502)
        return str(pr_url)

    def _run(self, args: list[str], cwd: Path | None = None) -> str:
        kwargs: dict[str, object] = {
            "text": True,
            "capture_output": True,
            "cwd": str(cwd) if cwd else None,
            "timeout": self.timeout,
        }
        if cwd is None:
            kwargs.pop("cwd")

        proc = subprocess.run(args, **kwargs)
        if proc.returncode != 0:
            output = (proc.stderr or proc.stdout or "").strip()
            raise GitHubSyncError(f"git command failed: {' '.join(args)}: {output}", status_code=502)
        return proc.stdout.strip()

    def create_pr(self, branch: str | None, commit_message: str, base: str = "origin/main") -> tuple[str, str]:
        workspace = self.ensure_repo()
        state = self.sync_state()
        if state.unstaged_files or state.untracked_files:
            raise GitHubSyncError("unstaged/untracked files exist. commit only staged changes for PR.", status_code=409)
        if not state.staged_files:
            raise GitHubSyncError("no staged changes found. run upsert_doc first.", status_code=409)

        safe_branch = self._validate_branch_name(branch.strip() if branch else f"knowledge-sync/{int(time.time())}")
        self._run(["git", "-C", str(workspace), "checkout", "-B", safe_branch], cwd=workspace)
        self._run(["git", "-C", str(workspace), "commit", "-m", commit_message], cwd=workspace)

        self._run(["git", "-C", str(workspace), "push", "-u", self.remote_name, safe_branch], cwd=workspace)
        pr_url = self._create_pull_request(safe_branch, base=base, title=commit_message)
        return safe_branch, pr_url

    def workspace_root(self) -> Path:
        return self.root.resolve()

    def ensure_repo(self) -> Path:
        workspace = self.workspace_root()
        if workspace.exists():
            if not (workspace / ".git").exists():
                raise GitHubSyncError(f"{workspace} exists but is not a git repository", status_code=409)
            self._run(["git", "remote", "set-url", self.remote_name, self._repo_url()], cwd=workspace)
            return workspace

        workspace.parent.mkdir(parents=True, exist_ok=True)
        self._run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                self.ref,
                self._repo_url(),
                str(workspace),
            ]
        )
        return workspace

    def _workspace_empty(self) -> bool:
        workspace = self.workspace_root()
        return not any(workspace.iterdir()) if workspace.exists() else True

    def sync_for_read(self) -> Path:
        workspace = self.ensure_repo()
        if self._has_local_changes(workspace):
            raise GitHubSyncError("local changes exist. commit or stash before pulling.", status_code=409)
        self._run(["git", "-C", str(workspace), "fetch", self.remote_name, "--prune", self.ref], cwd=workspace)
        self._run(["git", "-C", str(workspace), "checkout", self.ref], cwd=workspace)
        self._run(["git", "-C", str(workspace), "pull", "--ff-only", self.remote_name, self.ref], cwd=workspace)
        return workspace

    def stage_file(self, path: Path) -> None:
        workspace = self.ensure_repo()
        rel = str(path.resolve().relative_to(workspace))
        self._run(["git", "-C", str(workspace), "add", rel], cwd=workspace)

    def sync_state(self) -> GitHubSyncState:
        workspace = self.ensure_repo()
        branch = self._run(["git", "-C", str(workspace), "rev-parse", "--abbrev-ref", "HEAD"], cwd=workspace)
        remote = self._run(["git", "-C", str(workspace), "remote", "get-url", self.remote_name], cwd=workspace)
        raw = self._run(
            ["git", "-C", str(workspace), "status", "--short"],
            cwd=workspace,
        )
        branch_status = self._run(["git", "-C", str(workspace), "status", "--branch", "--short"], cwd=workspace)

        ahead = 0
        for line in branch_status.splitlines():
            if not line.startswith("## "):
                continue
            match = re.search(r"\[ahead (\d+)", line)
            if match:
                ahead = int(match.group(1))
            break

        staged: list[str] = []
        unstaged: list[str] = []
        untracked: list[str] = []
        for line in raw.splitlines():
            if len(line) < 3:
                continue
            index = line[0]
            worktree = line[1]
            path = line[3:]
            if index != " ":
                staged.append(path)
            if worktree != " " and worktree != "?":
                unstaged.append(path)
            if worktree == "?":
                untracked.append(path)

        return GitHubSyncState(
            branch=branch,
            workspace=workspace,
            remote_url=remote,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            has_unpushed_commits=ahead > 0,
        )

    @staticmethod
    def _has_local_changes(workspace: Path) -> bool:
        try:
            proc = subprocess.run(
                ["git", "-C", str(workspace), "status", "--short", "--untracked-files=no"],
                text=True,
                capture_output=True,
                timeout=10,
            )
            return bool(proc.stdout.strip())
        except OSError as exc:
            raise GitHubSyncError(f"git status failed: {exc}") from exc
