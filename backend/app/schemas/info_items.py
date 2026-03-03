from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InfoItemPublishIn(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_url: str | None = None
    published_at: datetime | None = None
    importance_score: int = Field(ge=1, le=5)
    is_new_tech: bool = False
    comment: str | None = None
    source_types: list[str] = Field(default_factory=list)
    info_types: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    domain_ids: list[str] = Field(min_length=1)
    classification: str | None = None


class InfoItemOut(BaseModel):
    id: UUID
    title: str
    content: str
    source_url: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    status: str
    importance_score: int
    is_new_tech: bool
    comment: str | None
    source_types: list[str]
    info_types: list[str]
    tags: list[str]
    domain_ids: list[str]
    classification: str | None

    model_config = {"from_attributes": True}
