from __future__ import annotations

from datetime import datetime
import re
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, Field, field_validator


class DocInfo(BaseModel):
    path: str
    size: int
    modified_at: datetime


class ListDocsInput(BaseModel):
    subdir: str | None = Field(default=None, description="Optional subdirectory under knowledge root")


class ListDocsOutput(BaseModel):
    docs: list[DocInfo]


class ReadDocInput(BaseModel):
    path: str


class ReadDocOutput(BaseModel):
    path: str
    content: str


class SearchDocsInput(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=200)
    case_sensitive: bool = False


class SearchHit(BaseModel):
    path: str
    line: int
    snippet: str


class SearchDocsOutput(BaseModel):
    hits: list[SearchHit]


class UpsertDocInput(BaseModel):
    path: str
    content: str
    mode: Literal["overwrite", "append"] = "overwrite"


class UpsertDocOutput(BaseModel):
    ok: bool
    path: str


class RebuildSummaryInput(BaseModel):
    paths: list[str] = Field(min_length=1)
    output_path: str
    style: Literal["notes", "spec", "faq"] = "notes"


class RebuildSummaryOutput(BaseModel):
    ok: bool
    output_path: str
    summary: str


class MCPCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MCPToolDef(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class MCPManifest(BaseModel):
    server_name: str
    version: str
    tools: list[MCPToolDef]


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
