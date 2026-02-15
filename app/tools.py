from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from .config import SETTINGS
from .schemas import (
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
from .security import SecurityError, resolve_relative_path


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



def _utc_iso(ts: float) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)



def _to_rel(path: Path) -> str:
    return str(path.relative_to(SETTINGS.knowledge_root))



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



def list_docs(payload: ListDocsInput) -> ListDocsOutput:
    base = SETTINGS.knowledge_root
    if payload.subdir:
        base = resolve_relative_path(payload.subdir, expect_file=False, must_exist=True)
        if not base.is_dir():
            raise ToolError("subdir must be a directory", status_code=400)

    docs = _all_docs_under(base)
    return ListDocsOutput(
        docs=[
            {
                "path": _to_rel(p),
                "size": p.stat().st_size,
                "modified_at": _utc_iso(p.stat().st_mtime),
            }
            for p in docs
        ]
    )



def read_doc(payload: ReadDocInput) -> ReadDocOutput:
    path = resolve_relative_path(payload.path, must_exist=True)
    size = path.stat().st_size
    if size > SETTINGS.max_read_bytes:
        raise ToolError(f"file too large ({size} bytes)", status_code=413)

    content = path.read_text(encoding="utf-8", errors="replace")
    return ReadDocOutput(path=_to_rel(path), content=content)



def search_docs(payload: SearchDocsInput) -> SearchDocsOutput:
    query = payload.query if payload.case_sensitive else payload.query.lower()
    hits: list[SearchHit] = []

    for doc in _all_docs_under(SETTINGS.knowledge_root):
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

    path = resolve_relative_path(payload.path, must_exist=False)
    path.parent.mkdir(parents=True, exist_ok=True)

    if payload.mode == "overwrite":
        path.write_text(payload.content, encoding="utf-8")
    else:
        with path.open("a", encoding="utf-8") as f:
            f.write(payload.content)

    return UpsertDocOutput(ok=True, path=_to_rel(path))



def rebuild_summary(payload: RebuildSummaryInput) -> RebuildSummaryOutput:
    if SETTINGS.read_only:
        raise ToolError("server is in read-only mode", status_code=403)

    docs: list[tuple[str, str]] = []
    for rel in payload.paths:
        doc = read_doc(ReadDocInput(path=rel))
        docs.append((doc.path, doc.content))

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
}



def manifest(server_name: str, version: str) -> list[MCPToolDef]:
    return [
        MCPToolDef(
            name=spec.name,
            description=spec.description,
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
    except SecurityError as exc:
        raise ToolError(str(exc), status_code=403) from exc
