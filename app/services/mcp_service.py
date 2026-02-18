from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from ..config import SETTINGS
from ..github_sync import GitHubSyncError
from ..models.document import (
    ListDocsInput,
    ListDocsOutput,
    ReadDocInput,
    ReadDocOutput,
    SearchDocsInput,
    SearchDocsOutput,
    UpsertDocInput,
    UpsertDocOutput,
)
from ..models.github import CreatePRInput, CreatePROutput, GitHubSyncStateInput, GitHubSyncStateOutput
from ..models.mcp import MCPToolDef
from ..models.summary import RebuildSummaryInput, RebuildSummaryOutput
from ..security import SecurityError
from .document_service import DocumentService, ToolError
from .github_service import GitHubService
from .summary_service import SummaryService


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: Callable[[BaseModel], BaseModel]


def describe_tool(spec: ToolSpec) -> str:
    description = spec.description
    if SETTINGS.backend == "github" and SETTINGS.github_repo and spec.name in {"list_docs", "read_doc", "search_docs"}:
        description = f"{description} (source: github:{SETTINGS.github_repo}@{SETTINGS.github_ref})"
    return description


TOOL_SPECS: dict[str, ToolSpec] = {
    "list_docs": ToolSpec(
        name="list_docs",
        description="List knowledge documents under an optional subdirectory",
        input_model=ListDocsInput,
        output_model=ListDocsOutput,
        handler=DocumentService.list_docs,
    ),
    "read_doc": ToolSpec(
        name="read_doc",
        description="Read one knowledge document",
        input_model=ReadDocInput,
        output_model=ReadDocOutput,
        handler=DocumentService.read_doc,
    ),
    "search_docs": ToolSpec(
        name="search_docs",
        description="Search all docs for a keyword and return matching lines",
        input_model=SearchDocsInput,
        output_model=SearchDocsOutput,
        handler=DocumentService.search_docs,
    ),
    "upsert_doc": ToolSpec(
        name="upsert_doc",
        description="Create or update a knowledge document",
        input_model=UpsertDocInput,
        output_model=UpsertDocOutput,
        handler=DocumentService.upsert_doc,
    ),
    "rebuild_summary": ToolSpec(
        name="rebuild_summary",
        description="Build a synthesized summary from multiple source documents",
        input_model=RebuildSummaryInput,
        output_model=RebuildSummaryOutput,
        handler=SummaryService.rebuild_summary,
    ),
    "sync_status": ToolSpec(
        name="sync_status",
        description="Show git workspace status for knowledge sync branch and PR readiness",
        input_model=GitHubSyncStateInput,
        output_model=GitHubSyncStateOutput,
        handler=GitHubService.sync_status,
    ),
    "create_pr": ToolSpec(
        name="create_pr",
        description="Commit staged changes on a new branch and create a GitHub PR, returning the PR URL",
        input_model=CreatePRInput,
        output_model=CreatePROutput,
        handler=GitHubService.create_pr,
    ),
}


class MCPService:
    DEFAULT_PROTOCOL_VERSION = "2025-11-25"

    @staticmethod
    def manifest(server_name: str, version: str) -> list[MCPToolDef]:
        return [
            MCPToolDef(
                name=spec.name,
                description=describe_tool(spec),
                input_schema=spec.input_model.model_json_schema(),
                output_schema=spec.output_model.model_json_schema(),
            )
            for spec in TOOL_SPECS.values()
        ]

    @staticmethod
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
        except GitHubSyncError as exc:
            raise ToolError(str(exc), status_code=exc.status_code) from exc
        except SecurityError as exc:
            raise ToolError(str(exc), status_code=403) from exc

    @staticmethod
    def handle_jsonrpc_method(method: str, params: dict[str, Any], server_name: str, server_version: str) -> dict[str, Any]:
        """Handle MCP JSON-RPC method calls."""
        if method == "initialize":
            protocol_version = params.get("protocolVersion") or MCPService.DEFAULT_PROTOCOL_VERSION
            return {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": server_name, "version": server_version},
            }
        
        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": spec.name,
                        "description": describe_tool(spec),
                        "inputSchema": spec.input_model.model_json_schema(),
                        "outputSchema": spec.output_model.model_json_schema(),
                    }
                    for spec in TOOL_SPECS.values()
                ]
            }
        
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            github_status = GitHubService.github_connection_probe() if SETTINGS.backend == "github" else {
                "connected": False, 
                "backend": SETTINGS.backend
            }
            
            model = MCPService.run_tool(name, arguments)
            structured = model.model_dump(mode="json")
            
            return {
                "content": [{"type": "text", "text": json.dumps(structured, ensure_ascii=False)}],
                "structuredContent": structured,
                "github": github_status,
                "isError": False,
            }
        
        elif method == "ping":
            return {}
        
        else:
            raise ToolError(f"Method not found: {method}", status_code=404)
