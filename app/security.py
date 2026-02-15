from __future__ import annotations

from pathlib import Path

from .config import SETTINGS


class SecurityError(ValueError):
    pass



def is_allowed_extension(path: Path) -> bool:
    return path.suffix.lower() in SETTINGS.allowed_extensions



def resolve_relative_path(path: str, *, expect_file: bool = True, must_exist: bool = False) -> Path:
    if not path or not path.strip():
        raise SecurityError("path is required")

    candidate = Path(path)
    if candidate.is_absolute():
        raise SecurityError("absolute paths are not allowed")

    resolved = (SETTINGS.knowledge_root / candidate).resolve()

    root = SETTINGS.knowledge_root
    if resolved != root and root not in resolved.parents:
        raise SecurityError("path escapes knowledge root")

    if must_exist and not resolved.exists():
        raise SecurityError("path does not exist")

    if expect_file and resolved.exists() and not resolved.is_file():
        raise SecurityError("path is not a file")

    if expect_file and not is_allowed_extension(resolved):
        raise SecurityError(
            f"unsupported file extension. allowed: {', '.join(SETTINGS.allowed_extensions)}"
        )

    return resolved
