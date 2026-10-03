from pydantic import BaseModel, Field


class JobMatchResponse(BaseModel):
    job_id: str
    job_title: str
    company: str

    overall_match_score: int | None = Field(default=None, ge=0, le=100)
    skill_match_score: int | None = Field(default=None, ge=0, le=100)
    experience_score: int | None = Field(default=None, ge=0, le=100)

    match_score: int = Field(ge=0, le=100)

    matched_skills: list[str]
    missing_skills: list[str]
    skills_available: bool

    experience_fit: str
    candidate_experience_years: float | None
    required_experience_min_years: float | None
    required_experience_max_years: float | None

    note: str