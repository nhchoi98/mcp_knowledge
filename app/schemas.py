from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DocInfo(BaseModel):
    path: str
    size: int
    modified_at: datetime


class ListDocsInput(BaseModel):
    subdir: str | None = Field(default=None, description="Optional subdirectory under knowledge root")


class ListDocsOutput(BaseModel):
    docs: list[DocInfo]


class ReadDocInput(BaseModel):
    path: str


class ReadDocOutput(BaseModel):
    path: str
    content: str


class SearchDocsInput(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=200)
    case_sensitive: bool = False


class SearchHit(BaseModel):
    path: str
    line: int
    snippet: str


class SearchDocsOutput(BaseModel):
    hits: list[SearchHit]


class UpsertDocInput(BaseModel):
    path: str
    content: str
    mode: Literal["overwrite", "append"] = "overwrite"


class UpsertDocOutput(BaseModel):
    ok: bool
    path: str


class RebuildSummaryInput(BaseModel):
    paths: list[str] = Field(min_length=1)
    output_path: str
    style: Literal["notes", "spec", "faq"] = "notes"


class RebuildSummaryOutput(BaseModel):
    ok: bool
    output_path: str
    summary: str


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
