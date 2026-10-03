from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    job_id: str | None = None
    status: str = Field(default="applied", min_length=1, max_length=30)
    applied_at: datetime
    notes: str | None = None
    follow_up_at: datetime | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )
    notes: str | None = None
    follow_up_at: datetime | None = None
    interview_at: datetime | None = None


class ApplicationResponse(BaseModel):
    id: str
    job_id: str | None
    title: str | None
    company: str | None
    status: str
    applied_at: datetime
    notes: str | None
    follow_up_at: datetime | None
    interview_at: datetime | None
