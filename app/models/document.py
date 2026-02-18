from __future__ import annotations

from datetime import datetime
from typing import Literal

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
