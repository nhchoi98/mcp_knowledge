from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator


class GitHubSyncStateInput(BaseModel):
    pass


class GitHubSyncStateOutput(BaseModel):
    branch: str
    workspace: str
    remote_url: str
    staged_files: list[str]
    unstaged_files: list[str]
    untracked_files: list[str]
    is_clean: bool
    ready_for_pr: bool
    has_unpushed_commits: bool
    push_command: str
    ready_for_pull: bool


class CreatePRInput(BaseModel):
    _branch_pattern: ClassVar = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
    _invalid_branch_pattern: ClassVar = re.compile(r"(\.\.)|(@\{)|[\\\s\^:\*\[\]\?]|~")
    min_branch_len: ClassVar[int] = 1
    max_branch_len: ClassVar[int] = 100

    branch: str | None = Field(default=None, description="Optional branch name. If empty, auto-generated.")
    commit_message: str = Field(default="Update knowledge", min_length=1, description="Commit message for PR branch")
    base: str = Field(default="origin/main", description="Base ref for PR compare URL")

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, value: str | None) -> str | None:
        if value is None:
            return None
        branch = value.strip()
        if not branch:
            raise ValueError("branch cannot be empty")
        if len(branch) < cls.min_branch_len or len(branch) > cls.max_branch_len:
            raise ValueError(f"branch length must be between {cls.min_branch_len} and {cls.max_branch_len}")
        if not cls._branch_pattern.fullmatch(branch):
            raise ValueError("branch contains invalid characters; allowed: A-Z a-z 0-9 . _ / -")
        if cls._invalid_branch_pattern.search(branch):
            raise ValueError("branch contains invalid git ref characters")
        if "//" in branch or ".." in branch or branch.startswith("-") or branch.endswith("-"):
            raise ValueError("branch cannot contain empty segments, '..', '//' or start/end with '-'")
        if branch.startswith("/") or branch.endswith("/"):
            raise ValueError("branch cannot start or end with '/'")
        if branch.endswith(".lock"):
            raise ValueError("branch cannot end with '.lock'")
        if branch[0] == "." or branch[-1] == ".":
            raise ValueError("branch cannot start or end with '.'")
        for part in branch.split("/"):
            if not part:
                raise ValueError("branch contains empty path segment")
            if part.startswith(".") or part.endswith("."):
                raise ValueError("branch components cannot start or end with '.'")
            if part.startswith("-"):
                raise ValueError("branch component cannot start with '-'")
        return branch


class CreatePROutput(BaseModel):
    ok: bool
    branch: str
    commit_message: str
    pr_url: str
    push_command: str
