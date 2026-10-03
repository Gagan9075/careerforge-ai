from uuid import UUID

from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    summary: str | None = None
    skills: str | None = None
    experience: str | None = None
    education: str | None = None
    projects: str | None = None


class ResumeUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    summary: str | None = None
    skills: str | None = None
    experience: str | None = None
    education: str | None = None
    projects: str | None = None


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    summary: str | None
    skills: str | None
    experience: str | None
    education: str | None
    projects: str | None

    model_config = {"from_attributes": True}