from pydantic import BaseModel


class SavedJobResponse(BaseModel):
    job_id: str
    message: str


class SavedJobItem(BaseModel):
    job_id: str
    title: str
    company: str
    location: str | None
    employment_type: str | None
    experience_level: str | None
    min_experience_years: float | None
    max_experience_years: float | None
    source: str
    source_url: str
    application_url: str | None