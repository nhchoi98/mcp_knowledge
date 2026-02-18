from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import SETTINGS
from ..github_sync import GitHubSyncManager
from ..models.document import (
    ListDocsInput,
    ListDocsOutput,
    ReadDocInput,
    ReadDocOutput,
    SearchDocsInput,
    SearchDocsOutput,
    SearchHit,
    UpsertDocInput,
    UpsertDocOutput,
)


class ToolError(RuntimeError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


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


class DocumentService:
    @staticmethod
    def list_docs(payload: ListDocsInput) -> ListDocsOutput:
        if SETTINGS.backend == "github":
            return ListDocsOutput(docs=_list_docs_github(payload.subdir))
        return ListDocsOutput(docs=_list_docs_local(payload.subdir))

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
