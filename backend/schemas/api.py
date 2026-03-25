from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


FieldType = Literal["string", "number", "date", "currency", "longtext"]


class Placeholder(BaseModel):
    key: str
    format: str
    slideIndex: int
    shapeName: str | None = None
    context: str
    suggestedType: FieldType


class ParseResponse(BaseModel):
    placeholders: list[Placeholder]


class FieldConfig(BaseModel):
    key: str
    label: str
    type: FieldType = "string"
    required: bool = False
    default: str | None = None
    group: str | None = None


class FillRequest(BaseModel):
    answers: dict[str, str | int | float | None]
    fieldConfig: list[FieldConfig] = Field(default_factory=list)
    keepUnfilled: bool = False


class JobResponse(BaseModel):
    id: str
    state: str
    error: str | None = None
    placeholders: list[Placeholder] = Field(default_factory=list)


class UploadResponse(BaseModel):
    jobId: str
    state: str
