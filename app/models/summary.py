from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RebuildSummaryInput(BaseModel):
    paths: list[str] = Field(min_length=1)
    output_path: str
    style: Literal["notes", "spec", "faq"] = "notes"


class RebuildSummaryOutput(BaseModel):
    ok: bool
    output_path: str
    summary: str
