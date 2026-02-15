#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys
from urllib.parse import quote, urlencode
from typing import Any
from urllib import error, request

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.config import SETTINGS  # noqa: E402


NOTION_VERSION = "2022-06-28"
NOTION_API_BASE = "https://api.notion.com/v1"


def _ensure_str(value: Any) -> str:
    return str(value) if value is not None else ""


def _normalize_notion_id(value: str) -> str:
    text = value.strip()
    if not text:
        raise RuntimeError("NOTION_ROOT_PAGE_ID is required")

    # 1) Notion 페이지 링크 또는 하이픈이 붙은 UUID 우선 매칭
    candidates = re.findall(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text)
    if not candidates:
        # 2) 하이픈 없는 32자리 UUID 후보
        candidates = re.findall(r"[0-9a-fA-F]{32}", text)

    if not candidates:
        raise RuntimeError(f"NOTION_ROOT_PAGE_ID format is invalid: {value}")

    if len(candidates) > 1:
        # notion URL 안에 page id + 다른 32자리 토큰이 같이 있는 경우가 드물게 있어
        # 이런 경우 잘못 매칭을 방지하려면 순수 32자리 ID만 입력하도록 요구
        raise RuntimeError(
            "NOTION_ROOT_PAGE_ID contains multiple page-id candidates. "
            "Please pass a single page id (uuid with/without dashes) only."
        )

    candidate = candidates[0].replace("-", "")
    if len(candidate) != 32:
        raise RuntimeError(f"NOTION_ROOT_PAGE_ID format is invalid: {value}")

    # Notion endpoints are more predictable with dashed UUID format.
    return f"{candidate[0:8]}-{candidate[8:12]}-{candidate[12:16]}-{candidate[16:20]}-{candidate[20:32]}"


def run_sync(
    notion_api_token: str | None = None,
    notion_root_page_id: str | None = None,
    notion_max_pages: int | None = None,
    notion_sync_subdir: str | None = None,
) -> list[str]:
    token = (notion_api_token or "").strip()
    root_page_id_raw = (notion_root_page_id or "").strip()
    subdir = (notion_sync_subdir or "").strip()

    if not token:
        token = SETTINGS.notion_api_token or ""
    if not root_page_id_raw:
        root_page_id_raw = SETTINGS.notion_root_page_id or ""
    if notion_max_pages is None:
        notion_max_pages = SETTINGS.notion_max_pages
    if not subdir:
        subdir = SETTINGS.notion_sync_subdir

    root_id = _normalize_notion_id(root_page_id_raw)
    if not token or not root_id:
        raise RuntimeError("NOTION_API_TOKEN and NOTION_ROOT_PAGE_ID are required")

    output_dir = SETTINGS.knowledge_root / subdir
    syncer = NotionSyncer(token=token, output_dir=output_dir, max_pages=notion_max_pages)
    return syncer.run(root_id)


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = text.strip("-")
    return text[:80] or "page"


def _plain_text(item: dict[str, Any]) -> str:
    return item.get("plain_text") or ""


def _rich_text_to_markdown(rich: list[dict[str, Any]]) -> str:
    return "".join(_plain_text(part) for part in rich or [])


def _get_title(page: dict[str, Any]) -> str:
    props = page.get("properties", {})
    if "title" in props and isinstance(props["title"], dict):
        title_items = props["title"].get("title", [])
        if title_items:
            return _rich_text_to_markdown(title_items)

    for value in props.values():
        if not isinstance(value, dict):
            continue
        t = value.get("type")
        if t in {"title", "name"}:
            key = "title" if t == "title" else "title"
            items = value.get(key) or []
            if items:
                return _rich_text_to_markdown(items)
    return "untitled"


class NotionSyncer:
    def __init__(self, token: str, output_dir: Path, max_pages: int = 0) -> None:
        self._token = token
        self._output_dir = output_dir
        self._max_pages = max_pages
        self._visited: set[str] = set()
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._sync_count = 0

    def _request_json(
        self, method: str, path: str, payload: dict[str, Any] | None = None, query: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{NOTION_API_BASE}{quote(path, safe='/')}"
        if query:
            url = f"{url}?{urlencode(query, doseq=True)}"
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=30) as res:
                return json.loads(res.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Notion API error {exc.code} on {url}: {body}") from exc

    def _fetch_page(self, page_id: str) -> dict[str, Any]:
        return self._request_json("GET", f"/pages/{page_id}")

    def _fetch_block_children(self, block_id: str) -> list[dict[str, Any]]:
        cursor = None
        children: list[dict[str, Any]] = []
        while True:
            query: dict[str, Any] = {"page_size": 100}
            if cursor:
                query["start_cursor"] = cursor
            resp = self._request_json("GET", f"/blocks/{block_id}/children", query=query)
            children.extend(resp.get("results", []))
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
            if not cursor:
                break
        return children

    def _write_file(self, page_id: str, title: str, markdown: str) -> str:
        safe = _slugify(_ensure_str(title))
        filename = f"{safe}-{page_id.replace('-', '')[:10]}.md"
        path = self._output_dir / filename
        path.write_text(
            "---\n"
            f"notion_id: {page_id}\n"
            f"title: {_ensure_str(title)}\n"
            "---\n\n"
            f"{markdown}\n",
            encoding="utf-8",
        )
        return str(path.relative_to(SETTINGS.knowledge_root))

    def _block_to_lines(self, block: dict[str, Any], level: int = 0) -> tuple[list[str], list[str]]:
        lines: list[str] = []
        child_pages: list[str] = []
        kind = block.get("type")
        data = block.get(kind, {}) if kind else {}
        indent = "  " * level

        def heading(n: int) -> None:
            text = _rich_text_to_markdown(data.get("rich_text", []))
            lines.append(f"{'#' * n} {text}")

        def paragraph() -> None:
            text = _rich_text_to_markdown(data.get("rich_text", []))
            if text:
                lines.append(f"{indent}{text}")

        def list_like(prefix: str) -> None:
            text = _rich_text_to_markdown(data.get("rich_text", []))
            lines.append(f"{indent}{prefix} {text}")

        if kind == "paragraph":
            paragraph()
        elif kind == "heading_1":
            heading(1)
        elif kind == "heading_2":
            heading(2)
        elif kind == "heading_3":
            heading(3)
        elif kind == "bulleted_list_item":
            list_like("-")
        elif kind == "numbered_list_item":
            list_like("1.")
        elif kind == "to_do":
            checked = bool(data.get("checked"))
            text = _rich_text_to_markdown(data.get("rich_text", []))
            lines.append(f"{indent}- [{'x' if checked else ' '}] {text}")
        elif kind == "quote":
            text = _rich_text_to_markdown(data.get("rich_text", []))
            lines.append(f"{indent}> {text}")
        elif kind == "code":
            lang = data.get("language", "text")
            text = _rich_text_to_markdown(data.get("rich_text", []))
            lines.append(f"{indent}```{lang}")
            lines.append(f"{indent}{text}")
            lines.append(f"{indent}```")
        elif kind == "divider":
            lines.append(f"{indent}---")
        elif kind == "child_page":
            title = _ensure_str(data.get("title", "child-page"))
            child_id = _ensure_str(block.get("id"))
            if child_id:
                child_pages.append(child_id)
                slug = _slugify(title)
                lines.append(f"{indent}- [child page: {title}](./{slug}.md)")
        elif kind == "child_database":
            title = _ensure_str(data.get("title", "child-database"))
            lines.append(f"{indent}- [child database: {title}]")
        else:
            text = _rich_text_to_markdown(data.get("rich_text", [])) if isinstance(data, dict) else ""
            if text:
                lines.append(f"{indent}{text}")

        return lines, child_pages

    def sync_page(self, page_id: str) -> str | None:
        if page_id in self._visited:
            return None
        self._visited.add(page_id)

        page = self._fetch_page(page_id)
        title = _get_title(page)

        lines: list[str] = [f"# {title}", ""]
        child_page_ids: list[str] = []

        for block in self._fetch_block_children(page_id):
            block_lines, children = self._block_to_lines(block)
            lines.extend(block_lines)
            child_page_ids.extend(children)
            child_block_id = block.get("id")
            if child_block_id and block.get("has_children"):
                nested_blocks = self._fetch_block_children(child_block_id)
                for nested in nested_blocks:
                    nested_lines, nested_children = self._block_to_lines(nested, level=1)
                    lines.extend(nested_lines)
                    child_page_ids.extend(nested_children)

        for child_id in child_page_ids:
            if child_id in self._visited:
                continue
            if self._max_pages and self._sync_count >= self._max_pages:
                continue
            child_title = None
            try:
                child_page = self._fetch_page(child_id)
                child_title = _get_title(child_page)
            except Exception:
                child_title = "child-page"
            lines.append("")
            lines.append(f"## {child_title}")
            lines.append(f"[See: {child_id} synced as linked file]")

            self._sync_count += 1
            self.sync_page(child_id)

        rel = self._write_file(page_id, title, "\n".join(lines))
        return rel

    def run(self, root_page_id: str) -> list[str]:
        self._sync_count = 1
        if self._max_pages and self._sync_count > self._max_pages:
            return []
        result = self.sync_page(root_page_id)
        if result is None:
            return []
        return [result]


def main() -> int:
    synced = run_sync()

    if synced:
        print("Synced:")
        for path in synced:
            print(f"- {path}")
        return 0

    print("No pages were synced.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
