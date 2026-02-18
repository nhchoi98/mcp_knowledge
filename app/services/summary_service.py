from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..config import SETTINGS
from ..models.summary import RebuildSummaryInput, RebuildSummaryOutput
from .document_service import (
    ToolError,
    _all_docs_under,
    _base_root,
    _resolve_local_path,
    _to_rel,
)
from ..models.document import UpsertDocInput
from .document_service import DocumentService


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


class SummaryService:
    @staticmethod
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
        written = DocumentService.upsert_doc(UpsertDocInput(path=payload.output_path, content=summary, mode="overwrite"))
        return RebuildSummaryOutput(ok=True, output_path=written.path, summary=summary)
