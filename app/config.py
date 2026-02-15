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
    knowledge_root: Path
    allowed_extensions: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    read_only: bool
    api_token: str | None
    max_read_bytes: int



def _discover_git_root(start_dir: Path | None = None) -> Path:
    current = (start_dir or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current



def load_settings() -> Settings:
    raw_root = os.getenv("KNOWLEDGE_ROOT")
    if raw_root:
        root = Path(raw_root).expanduser().resolve()
    elif _parse_bool(os.getenv("USE_GIT_ROOT"), default=False):
        root = _discover_git_root()
    else:
        root = Path("~/knowledge").expanduser().resolve()

    extensions_raw = os.getenv("ALLOWED_EXTENSIONS", ".md,.txt")
    extensions = tuple(sorted({ext.strip().lower() for ext in extensions_raw.split(",") if ext.strip()}))

    if not extensions:
        extensions = (".md", ".txt")

    token = os.getenv("MCP_API_TOKEN")
    if token:
        token = token.strip()

    origins_raw = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost,http://127.0.0.1,https://localhost,https://127.0.0.1",
    )
    origins = tuple(sorted({o.strip() for o in origins_raw.split(",") if o.strip()}))

    return Settings(
        knowledge_root=root,
        allowed_extensions=extensions,
        allowed_origins=origins,
        read_only=_parse_bool(os.getenv("READ_ONLY"), default=False),
        api_token=token or None,
        max_read_bytes=int(os.getenv("MAX_READ_BYTES", "2000000")),
    )


SETTINGS = load_settings()
