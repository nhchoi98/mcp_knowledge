from __future__ import annotations

import json
from urllib.parse import urlparse
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from .config import SETTINGS
from .schemas import MCPCallRequest, MCPManifest
from .tools import TOOL_SPECS, ToolError, manifest, run_tool

SERVER_NAME = "local-knowledge-mcp"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2025-11-25"

app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION)


def require_token(authorization: str | None = Header(default=None)) -> None:
    token = SETTINGS.api_token
    if not token:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")

    provided = authorization.split(" ", 1)[1].strip()
    if provided != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bearer token")


def _is_origin_allowed(origin: str) -> bool:
    if not origin or origin == "null":
        return True
    if origin in SETTINGS.allowed_origins:
        return True

    parsed = urlparse(origin)
    if parsed.scheme and parsed.hostname:
        if f"{parsed.scheme}://{parsed.hostname}" in SETTINGS.allowed_origins:
            return True

        with_port = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}" if parsed.port else None
        if with_port and with_port in SETTINGS.allowed_origins:
            return True

        for candidate in SETTINGS.allowed_origins:
            if candidate.endswith(":*") and f"{parsed.scheme}://{parsed.hostname}" == candidate[:-2]:
                return True

    return False


def require_origin(origin: str | None = Header(default=None)) -> None:
    if not _is_origin_allowed(origin or ""):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="origin not allowed")


def _event_stream():
    async def event_stream():
        data = {
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "tools": [name for name in TOOL_SPECS.keys()],
        }
        yield f"event: manifest\ndata: {json.dumps(data)}\n\n"
        while True:
            yield "event: heartbeat\ndata: {}\n\n"
            await __import__("asyncio").sleep(15)

    return event_stream()


@app.on_event("startup")
def _startup() -> None:
    SETTINGS.knowledge_root.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "knowledge_root": str(SETTINGS.knowledge_root),
        "read_only": SETTINGS.read_only,
        "tool_count": len(TOOL_SPECS),
    }


@app.get("/mcp/manifest", dependencies=[Depends(require_token), Depends(require_origin)])
def mcp_manifest() -> MCPManifest:
    return MCPManifest(server_name=SERVER_NAME, version=SERVER_VERSION, tools=manifest(SERVER_NAME, SERVER_VERSION))


@app.post("/mcp/call", dependencies=[Depends(require_token), Depends(require_origin)])
def mcp_call(payload: MCPCallRequest) -> dict[str, Any]:
    try:
        result = run_tool(payload.name, payload.arguments)
    except ToolError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    return {"ok": True, "tool": payload.name, "result": result.model_dump(mode="json")}


@app.get("/mcp/sse", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_sse() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type="text/event-stream")


@app.post("/mcp/sse", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_sse_post() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type="text/event-stream")


@app.get("/mcp", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_get() -> StreamingResponse:
    return StreamingResponse(_event_stream(), media_type="text/event-stream")


@app.post("/mcp", dependencies=[Depends(require_token), Depends(require_origin)])
async def mcp_jsonrpc(request: Request) -> JSONResponse:
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

    if req_id is None and method.startswith("notifications/"):
        return JSONResponse(status_code=202, content={})

    try:
        if method == "initialize":
            protocol_version = params.get("protocolVersion") or DEFAULT_PROTOCOL_VERSION
            result = {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        elif method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": spec.name,
                        "description": spec.description,
                        "inputSchema": spec.input_model.model_json_schema(),
                        "outputSchema": spec.output_model.model_json_schema(),
                    }
                    for spec in TOOL_SPECS.values()
                ]
            }
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            model = run_tool(name, arguments)
            structured = model.model_dump(mode="json")
            result = {
                "content": [{"type": "text", "text": json.dumps(structured, ensure_ascii=False)}],
                "structuredContent": structured,
                "isError": False,
            }
        elif method == "ping":
            result = {}
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                },
            )
    except ToolError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(exc)},
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32099, "message": f"Internal error: {exc}"},
            },
        )

    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": result})
