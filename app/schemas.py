from __future__ import annotations

# This module is kept for backwards compatibility
# All models have been moved to app.models

from .models import (
    CreatePRInput,
    CreatePROutput,
    DocInfo,
    GitHubSyncStateInput,
    GitHubSyncStateOutput,
    ListDocsInput,
    ListDocsOutput,
    MCPCallRequest,
    MCPManifest,
    MCPToolDef,
    ReadDocInput,
    ReadDocOutput,
    RebuildSummaryInput,
    RebuildSummaryOutput,
    SearchDocsInput,
    SearchDocsOutput,
    SearchHit,
    UpsertDocInput,
    UpsertDocOutput,
)

__all__ = [
    "CreatePRInput",
    "CreatePROutput",
    "DocInfo",
    "GitHubSyncStateInput",
    "GitHubSyncStateOutput",
    "ListDocsInput",
    "ListDocsOutput",
    "MCPCallRequest",
    "MCPManifest",
    "MCPToolDef",
    "ReadDocInput",
    "ReadDocOutput",
    "RebuildSummaryInput",
    "RebuildSummaryOutput",
    "SearchDocsInput",
    "SearchDocsOutput",
    "SearchHit",
    "UpsertDocInput",
    "UpsertDocOutput",
]

