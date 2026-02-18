from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MCPCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MCPToolDef(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class MCPManifest(BaseModel):
    server_name: str
    version: str
    tools: list[MCPToolDef]
