from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    backend: str
    knowledge_root: Path
    allowed_extensions: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    read_only: bool
    api_token: str | None
    github_repo: str | None
    github_ref: str
    github_token: str | None
    github_timeout_seconds: float
    notion_api_token: str | None
    notion_root_page_id: str | None
    notion_sync_subdir: str
    notion_max_pages: int
    max_read_bytes: int


def _load_env_file(project_root: Path) -> dict[str, str]:
    paths = (project_root / "env" / ".env", project_root / ".env")
    env_map: dict[str, str] = {}
    for path in paths:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            if (value.startswith("\"") and value.endswith("\"")) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            env_map[key] = value
        break
    return env_map

def _discover_git_root(start_dir: Path | None = None) -> Path:
    current = (start_dir or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current



def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parent.parent
    env_map = _load_env_file(project_root)

    def _get(name: str, default: str | None = None) -> str | None:
        if name in env_map:
            return env_map[name]
        return os.getenv(name, default)

    backend = (_get("KNOWLEDGE_BACKEND", "local") or "local").strip().lower()
    if backend not in {"local", "github"}:
        backend = "local"

    if backend == "github":
        # GitHub backend does not use a local knowledge directory.
        root = project_root
    else:
        raw_root = _get("KNOWLEDGE_ROOT")
        if raw_root:
            root = Path(raw_root).expanduser().resolve()
        elif _parse_bool(_get("USE_GIT_ROOT"), default=False):
            root = _discover_git_root()
        else:
            root = Path("~/knowledge").expanduser().resolve()

    extensions_raw = _get("ALLOWED_EXTENSIONS", ".md,.txt")
    extensions = tuple(sorted({ext.strip().lower() for ext in extensions_raw.split(",") if ext.strip()}))

    if not extensions:
        extensions = (".md", ".txt")

    token = _get("MCP_API_TOKEN")
    if token:
        token = token.strip()

    github_repo = _get("GITHUB_REPO")
    if github_repo:
        github_repo = github_repo.strip() or None

    github_ref = (_get("GITHUB_REF", "main") or "main").strip()
    github_token = _get("GITHUB_TOKEN")
    if github_token:
        github_token = github_token.strip() or None

    origins_raw = _get(
        "ALLOWED_ORIGINS",
        "http://localhost,http://127.0.0.1,https://localhost,https://127.0.0.1",
    )
    origins = tuple(sorted({o.strip() for o in origins_raw.split(",") if o.strip()}))

    notion_api_token = _get("NOTION_API_TOKEN")
    if notion_api_token:
        notion_api_token = notion_api_token.strip() or None

    notion_root_page_id = _get("NOTION_ROOT_PAGE_ID")
    if notion_root_page_id:
        notion_root_page_id = notion_root_page_id.strip() or None

    notion_sync_subdir = _get("NOTION_SYNC_SUBDIR", "notion").strip() or "notion"
    notion_max_pages = int(_get("NOTION_MAX_PAGES", "0") or "0")

    return Settings(
        backend=backend,
        knowledge_root=root,
        allowed_extensions=extensions,
        allowed_origins=origins,
        read_only=_parse_bool(_get("READ_ONLY"), default=False),
        api_token=token or None,
        github_repo=github_repo,
        github_ref=github_ref,
        github_token=github_token,
        github_timeout_seconds=float(_get("GITHUB_TIMEOUT_SECONDS", "15") or "15"),
        notion_api_token=notion_api_token,
        notion_root_page_id=notion_root_page_id,
        notion_sync_subdir=notion_sync_subdir,
        notion_max_pages=notion_max_pages,
        max_read_bytes=int(_get("MAX_READ_BYTES", "2000000")),
    )


SETTINGS = load_settings()
