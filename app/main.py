from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from .config import SETTINGS
from .models import MCPCallRequest, MCPManifest
from .services import AuthService, MCPService, GitHubService, ToolError, TOOL_SPECS

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

SERVER_NAME = "local-knowledge-mcp"
SERVER_VERSION = "0.1.0"
MEDIA_TYPE_SSE = "text/event-stream"

app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION)


def require_token(authorization: str | None = Header(default=None)) -> None:
    """Dependency for validating bearer token."""
    if not AuthService.validate_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing or invalid bearer token")


def require_origin(origin: str | None = Header(default=None)) -> None:
    """Dependency for validating CORS origin."""
    if not AuthService.is_origin_allowed(origin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="origin not allowed")


def _event_stream():
    """Generate SSE event stream for MCP."""
    async def event_stream():
        data = {
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "tools": list(TOOL_SPECS.keys()),
        }
        yield f"event: manifest\ndata: {json.dumps(data)}\n\n"
        while True:
            yield "event: heartbeat\ndata: {}\n\n"
            await __import__("asyncio").sleep(15)

    return event_stream()


@app.on_event("startup")
def _startup() -> None:
    if SETTINGS.backend == "local":
        SETTINGS.knowledge_root.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict[str, Any]:
    github_status = GitHubService.github_connection_probe() if SETTINGS.backend == "github" else {"connected": False, "backend": SETTINGS.backend}
    return {
        "ok": True,
        "backend": SETTINGS.backend,
        "knowledge_root": str(SETTINGS.knowledge_root),
        "github_repo": SETTINGS.github_repo,
        "github_ref": SETTINGS.github_ref,
        "github_status": github_status,
        "read_only": SETTINGS.read_only,
        "tool_count": len(TOOL_SPECS),
    }


@app.get("/mcp/manifest", dependencies=[Depends(require_token), Depends(require_origin)])
def mcp_manifest() -> MCPManifest:
    return MCPManifest(server_name=SERVER_NAME, version=SERVER_VERSION, tools=MCPService.manifest(SERVER_NAME, SERVER_VERSION))


@app.post("/mcp/call", dependencies=[Depends(require_token), Depends(require_origin)])
def mcp_call(payload: MCPCallRequest) -> dict[str, Any]:
    github_status = GitHubService.github_connection_probe() if SETTINGS.backend == "github" else {"connected": False, "backend": SETTINGS.backend}
    logger.info(
        f"MCP Call - Tool: {payload.name}, Arguments: {payload.arguments}, github_connected: {github_status.get('connected')}"
    )
    try:
        result = MCPService.run_tool(payload.name, payload.arguments)
        logger.info(f"MCP Call Success - Tool: {payload.name}")
    except ToolError as exc:
        logger.error(f"MCP Call Error - Tool: {payload.name}, Error: {str(exc)}")
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    return {"ok": True, "tool": payload.name, "result": result.model_dump(mode="json"), "github_status": github_status}


@app.get("/mcp/sse", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_sse() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type=MEDIA_TYPE_SSE)


@app.post("/mcp/sse", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_sse_post() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type=MEDIA_TYPE_SSE)


@app.get("/mcp", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_get() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type=MEDIA_TYPE_SSE)


@app.post("/mcp", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_jsonrpc(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC requests."""
    # Parse request body
    try:
        body = await request.json()
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}},
        )

    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}},
        )

    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    if not isinstance(method, str):
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid method"}},
        )

    # Handle notifications (requests without id)
    if req_id is None and method.startswith("notifications/"):
        return JSONResponse(status_code=202, content={})

    # Process method
    try:
        logger.info(f"MCP JSON-RPC - Method: {method}, Params: {params}")
        result = MCPService.handle_jsonrpc_method(method, params, SERVER_NAME, SERVER_VERSION)
        logger.info(f"MCP JSON-RPC Success - Method: {method}")
    except ToolError as exc:
        logger.error(f"MCP Tool Error - Method: {method}, Error: {str(exc)}")
        status_code = 404 if exc.status_code == 404 else 400
        error_code = -32601 if exc.status_code == 404 else -32000
        return JSONResponse(
            status_code=status_code,
            content={
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": error_code, "message": str(exc)},
            },
        )
    except Exception as exc:
        logger.error(f"MCP Internal Error - Method: {method}, Error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32099, "message": f"Internal error: {exc}"},
            },
        )

    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": result})
