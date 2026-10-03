from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    company: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    description: str = Field(min_length=1)
    skills: str | None = None
    employment_type: str | None = Field(default=None, max_length=50)
    experience_level: str | None = Field(default=None, max_length=100)

    min_experience_years: float | None = None
    max_experience_years: float | None = None

    source: str = Field(min_length=1, max_length=100)
    source_url: str = Field(min_length=1, max_length=500)
    application_url: str | None = Field(default=None, max_length=500)
    posted_at: datetime | None = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    location: str | None
    description: str
    skills: str | None
    employment_type: str | None
    experience_level: str | None
    min_experience_years: float | None
    max_experience_years: float | None
    source: str
    source_url: str
    application_url: str | None
    posted_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime