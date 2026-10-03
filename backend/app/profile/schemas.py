from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ProfileCreate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=150)
    college: str | None = Field(default=None, max_length=200)
    degree: str | None = Field(default=None, max_length=100)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    skills: str | None = None
    bio: str | None = None
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    phone: str | None
    location: str | None
    college: str | None
    degree: str | None
    graduation_year: int | None
    skills: str | None
    bio: str | None
    github_url: str | None
    linkedin_url: str | None
    portfolio_url: str | None

    model_config = {
        "from_attributes": True
    }

class ProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=150)
    college: str | None = Field(default=None, max_length=200)
    degree: str | None = Field(default=None, max_length=100)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    skills: str | None = None
    bio: str | None = None
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None