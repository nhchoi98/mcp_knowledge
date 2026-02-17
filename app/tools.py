from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from .config import SETTINGS
from .github_sync import GitHubSyncError, GitHubSyncManager
from .schemas import (
    GitHubSyncStateInput,
    GitHubSyncStateOutput,
    CreatePRInput,
    CreatePROutput,
    ListDocsInput,
    ListDocsOutput,
    MCPToolDef,
    ReadDocInput,
    ReadDocOutput,
    RebuildSummaryInput,
    RebuildSummaryOutput,
    SearchDocsInput,
    SearchDocsOutput,
    SearchHit,
    UpsertDocInput,
    UpsertDocOutput,
)
from .security import SecurityError


class ToolError(RuntimeError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: Callable[[BaseModel], BaseModel]


def describe_tool(spec: ToolSpec) -> str:
    description = spec.description
    if SETTINGS.backend == "github" and SETTINGS.github_repo and spec.name in {"list_docs", "read_doc", "search_docs"}:
        description = f"{description} (source: github:{SETTINGS.github_repo}@{SETTINGS.github_ref})"
    return description


_github_sync: GitHubSyncManager | None = None


def _github() -> GitHubSyncManager:
    global _github_sync
    if _github_sync is None:
        _github_sync = GitHubSyncManager()
    return _github_sync


def _utc_iso(ts: float) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _to_rel(path: Path) -> str:
    if SETTINGS.backend == "github":
        return str(path.relative_to(_github().workspace_root()))
    return str(path.relative_to(SETTINGS.knowledge_root))


def _safe_rel(raw: str) -> str:
    if not raw or not raw.strip():
        raise ToolError("path is required", status_code=400)
    clean = raw.strip().strip("/")
    if clean.startswith("..") or "/../" in clean:
        raise ToolError("path traversal is not allowed", status_code=400)
    return clean


def _resolve_local_path(
    path: str,
    *,
    expect_file: bool = True,
    must_exist: bool = True,
    base: Path,
) -> Path:
    clean = _safe_rel(path)
    root = base.resolve()
    candidate = (base / clean).resolve()
    if candidate != root and root not in candidate.parents:
        raise ToolError(f"path escapes knowledge root: {path}", status_code=400)

    if must_exist and not candidate.exists():
        raise ToolError(f"path does not exist: {path}", status_code=400)
    if expect_file and candidate.exists() and not candidate.is_file():
        raise ToolError(f"path is not a file: {path}", status_code=400)
    if expect_file and candidate.suffix.lower() not in SETTINGS.allowed_extensions:
        raise ToolError(
            f"unsupported file extension. allowed: {', '.join(SETTINGS.allowed_extensions)}",
            status_code=400,
        )
    return candidate


def _base_root() -> Path:
    if SETTINGS.backend == "github":
        return _github().workspace_root()
    return SETTINGS.knowledge_root


def _all_docs_under(base: Path) -> list[Path]:
    docs: list[Path] = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in SETTINGS.allowed_extensions:
            continue
        docs.append(p)
    docs.sort()
    return docs


def _ensure_github_repo_synced() -> Path:
    return _github().sync_for_read()


def _list_docs_local(subdir: str | None) -> list[dict[str, Any]]:
    base = SETTINGS.knowledge_root
    if subdir:
        base = _resolve_local_path(subdir, expect_file=False, must_exist=True, base=SETTINGS.knowledge_root)
        if not base.is_dir():
            raise ToolError("subdir must be a directory", status_code=400)

    docs = _all_docs_under(base)
    return [
        {
            "path": _to_rel(p),
            "size": p.stat().st_size,
            "modified_at": _utc_iso(p.stat().st_mtime),
        }
        for p in docs
    ]


def _list_docs_github(subdir: str | None) -> list[dict[str, Any]]:
    repo_root = _ensure_github_repo_synced()
    base = repo_root
    if subdir:
        safe_subdir = _safe_rel(subdir)
        base = (repo_root / safe_subdir).resolve()
        if not base.exists():
            raise ToolError(f"knowledge folder does not exist: {subdir}", status_code=404)
        if base != repo_root and repo_root not in base.parents:
            raise ToolError("subdir escapes knowledge repo", status_code=400)

    docs = _all_docs_under(base)
    return [{"path": _to_rel(p), "size": p.stat().st_size, "modified_at": _utc_iso(p.stat().st_mtime)} for p in docs]


def _extract_points(content: str, max_points: int = 5) -> list[str]:
    points: list[str] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            points.append(line.lstrip("# ").strip())
        elif line.startswith(("-", "*", "+")):
            points.append(line[1:].strip())
        elif len(line) > 24:
            points.append(line[:160])
        if len(points) >= max_points:
            break
    if not points:
        points.append("(No salient lines found)")
    return points


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


def list_docs(payload: ListDocsInput) -> ListDocsOutput:
    if SETTINGS.backend == "github":
        return ListDocsOutput(docs=_list_docs_github(payload.subdir))
    return ListDocsOutput(docs=_list_docs_local(payload.subdir))


def read_doc(payload: ReadDocInput) -> ReadDocOutput:
    if SETTINGS.backend == "github":
        base = _ensure_github_repo_synced()
    else:
        base = _base_root()
    path = _resolve_local_path(payload.path, must_exist=True, expect_file=True, base=base)
    size = path.stat().st_size
    if size > SETTINGS.max_read_bytes:
        raise ToolError(f"file too large ({size} bytes)", status_code=413)

    content = path.read_text(encoding="utf-8", errors="replace")
    return ReadDocOutput(path=_to_rel(path), content=content)


def search_docs(payload: SearchDocsInput) -> SearchDocsOutput:
    query = payload.query if payload.case_sensitive else payload.query.lower()
    hits: list[SearchHit] = []

    if SETTINGS.backend == "github":
        base = _ensure_github_repo_synced()
        docs = _all_docs_under(base)
    else:
        docs = _all_docs_under(SETTINGS.knowledge_root)

    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for idx, raw in enumerate(text.splitlines(), start=1):
            target = raw if payload.case_sensitive else raw.lower()
            if query in target:
                hits.append(
                    SearchHit(
                        path=_to_rel(doc),
                        line=idx,
                        snippet=raw.strip()[:200],
                    )
                )
                if len(hits) >= payload.limit:
                    return SearchDocsOutput(hits=hits)

    return SearchDocsOutput(hits=hits)


def upsert_doc(payload: UpsertDocInput) -> UpsertDocOutput:
    if SETTINGS.read_only:
        raise ToolError("server is in read-only mode", status_code=403)

    if SETTINGS.backend == "github":
        _github().ensure_repo()

    path = _resolve_local_path(
        payload.path,
        expect_file=False,
        must_exist=False,
        base=_base_root(),
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    if payload.mode == "overwrite":
        path.write_text(payload.content, encoding="utf-8")
    else:
        with path.open("a", encoding="utf-8") as f:
            f.write(payload.content)

    if SETTINGS.backend == "github":
        _github().stage_file(path)

    return UpsertDocOutput(ok=True, path=_to_rel(path))


def rebuild_summary(payload: RebuildSummaryInput) -> RebuildSummaryOutput:
    if SETTINGS.read_only:
        raise ToolError("server is in read-only mode", status_code=403)

    base_root = _base_root()
    docs: list[tuple[str, str]] = []
    invalid: list[str] = []
    for rel in payload.paths:
        normalized = rel.lstrip("/")
        try:
            candidate = _resolve_local_path(normalized, expect_file=False, must_exist=True, base=base_root)
        except ToolError as exc:
            invalid.append(f"{rel} ({exc})")
            continue

        if candidate.is_dir():
            source_docs = _all_docs_under(candidate)
            if not source_docs:
                invalid.append(f"{rel} (empty directory)")
                continue
            for p in source_docs:
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                except OSError as exc:
                    invalid.append(f"{_to_rel(p)} ({exc})")
                    continue
                docs.append((_to_rel(p), content))
            continue

        if candidate.suffix.lower() not in SETTINGS.allowed_extensions:
            invalid.append(f"{rel} (unsupported extension)")
            continue

        try:
            content = candidate.read_text(encoding="utf-8", errors="replace")
            docs.append((_to_rel(candidate), content))
        except OSError as exc:
            invalid.append(f"{rel} ({exc})")
            continue

    if not docs:
        raise ToolError(
            "rebuild_summary received no valid files. "
            "Use list_docs with files or directories that contain .md/.txt files. invalid paths: "
            + ", ".join(invalid[:20])
        )

    now = datetime.now(timezone.utc).isoformat()
    lines: list[str] = [f"# Rebuilt Summary ({payload.style})", "", f"Generated at: {now}", ""]

    if payload.style == "notes":
        for rel, content in docs:
            lines.append(f"## {rel}")
            for point in _extract_points(content):
                lines.append(f"- {point}")
            lines.append("")
    elif payload.style == "spec":
        lines.extend(["## Scope", ""])
        lines.append(f"- Source docs: {', '.join(rel for rel, _ in docs)}")
        lines.extend(["", "## Requirements", ""])
        for rel, content in docs:
            for point in _extract_points(content, max_points=3):
                lines.append(f"- [{rel}] {point}")
        lines.extend(["", "## Open Questions", "", "- Validate assumptions with domain owner.", ""])
    else:
        for rel, content in docs:
            lines.append(f"## Q: What is important in `{rel}`?")
            answer = "; ".join(_extract_points(content, max_points=4))
            lines.append(f"A: {answer}")
            lines.append("")

    summary = "\n".join(lines).rstrip() + "\n"
    written = upsert_doc(UpsertDocInput(path=payload.output_path, content=summary, mode="overwrite"))
    return RebuildSummaryOutput(ok=True, output_path=written.path, summary=summary)


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
TOOL_SPECS: dict[str, ToolSpec] = {
    "list_docs": ToolSpec(
        name="list_docs",
        description="List knowledge documents under an optional subdirectory",
        input_model=ListDocsInput,
        output_model=ListDocsOutput,
        handler=list_docs,
    ),
    "read_doc": ToolSpec(
        name="read_doc",
        description="Read one knowledge document",
        input_model=ReadDocInput,
        output_model=ReadDocOutput,
        handler=read_doc,
    ),
    "search_docs": ToolSpec(
        name="search_docs",
        description="Search all docs for a keyword and return matching lines",
        input_model=SearchDocsInput,
        output_model=SearchDocsOutput,
        handler=search_docs,
    ),
    "upsert_doc": ToolSpec(
        name="upsert_doc",
        description="Create or update a knowledge document",
        input_model=UpsertDocInput,
        output_model=UpsertDocOutput,
        handler=upsert_doc,
    ),
    "rebuild_summary": ToolSpec(
        name="rebuild_summary",
        description="Build a synthesized summary from multiple source documents",
        input_model=RebuildSummaryInput,
        output_model=RebuildSummaryOutput,
        handler=rebuild_summary,
    ),
    "sync_status": ToolSpec(
        name="sync_status",
        description="Show git workspace status for knowledge sync branch and PR readiness",
        input_model=GitHubSyncStateInput,
        output_model=GitHubSyncStateOutput,
        handler=sync_status,
    ),
    "create_pr": ToolSpec(
        name="create_pr",
        description="Commit staged changes on a new branch and create a GitHub PR, returning the PR URL",
        input_model=CreatePRInput,
        output_model=CreatePROutput,
        handler=create_pr,
    ),
}


def manifest(server_name: str, version: str) -> list[MCPToolDef]:
    return [
        MCPToolDef(
            name=spec.name,
            description=describe_tool(spec),
            input_schema=spec.input_model.model_json_schema(),
            output_schema=spec.output_model.model_json_schema(),
        )
        for spec in TOOL_SPECS.values()
    ]


def run_tool(name: str, arguments: dict[str, Any]) -> BaseModel:
    spec = TOOL_SPECS.get(name)
    if not spec:
        raise ToolError(f"unknown tool: {name}", status_code=404)

    try:
        payload = spec.input_model.model_validate(arguments)
    except Exception as exc:
        raise ToolError(f"invalid arguments for {name}: {exc}", status_code=422) from exc

    try:
        return spec.handler(payload)
    except GitHubSyncError as exc:
        raise ToolError(str(exc), status_code=exc.status_code) from exc
    except SecurityError as exc:
        raise ToolError(str(exc), status_code=403) from exc
