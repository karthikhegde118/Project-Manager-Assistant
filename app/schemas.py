from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class MeetingSummary(BaseModel):
    summary: str
    decisions: list[str] = Field(default_factory=list)
    risks_blockers: list[str] = Field(default_factory=list)


class TaskSource(BaseModel):
    type: Literal["notes", "transcript"]
    quote: str


class TaskItem(BaseModel):
    title: str
    project: str | None = None
    due_date: date | None = None
    due_date_confidence: float = 0.0
    priority: Literal["low", "medium", "high"] = "medium"
    status: Literal["proposed"] = "proposed"
    confidence: float = 0.0
    source: TaskSource
    tags: list[str] = Field(default_factory=list)


class FollowUp(BaseModel):
    title: str
    when: date | None = None
    source_quote: str


class QualitySection(BaseModel):
    missing_info_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ExtractionResponse(BaseModel):
    meeting_summary: MeetingSummary
    tasks: list[TaskItem] = Field(default_factory=list)
    follow_ups: list[FollowUp] = Field(default_factory=list)
    quality: QualitySection
