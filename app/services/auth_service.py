from __future__ import annotations

from urllib.parse import urlparse

from ..config import SETTINGS


class AuthService:
    @staticmethod
    def validate_token(authorization: str | None) -> bool:
        """Validate bearer token. Returns True if valid or no token required."""
        token = SETTINGS.api_token
        if not token:
            return True

        if not authorization or not authorization.startswith("Bearer "):
            return False

        provided = authorization.split(" ", 1)[1].strip()
        return provided == token

    @staticmethod
    def is_origin_allowed(origin: str | None) -> bool:
        """Check if the origin is allowed based on CORS settings."""
        if not origin or origin == "null":
            return True
        
        if origin in SETTINGS.allowed_origins:
            return True

        parsed = urlparse(origin)
        if not parsed.scheme or not parsed.hostname:
            return False

        # Check exact match with scheme://hostname
        base_origin = f"{parsed.scheme}://{parsed.hostname}"
        if base_origin in SETTINGS.allowed_origins:
            return True

        # Check with port
        if parsed.port:
            with_port = f"{base_origin}:{parsed.port}"
            if with_port in SETTINGS.allowed_origins:
                return True

        # Check wildcard port patterns (e.g., "http://localhost:*")
        for candidate in SETTINGS.allowed_origins:
            if candidate.endswith(":*") and base_origin.startswith(candidate[:-2]):
                return True

        return False
