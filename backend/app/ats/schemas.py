from pydantic import BaseModel, Field


class ATSScoreResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)

    completeness_score: int = Field(ge=0, le=20)
    skills_score: int = Field(ge=0, le=20)
    experience_score: int = Field(ge=0, le=15)
    projects_score: int = Field(ge=0, le=15)
    education_score: int = Field(ge=0, le=10)
    certifications_score: int = Field(ge=0, le=5)
    structure_score: int = Field(ge=0, le=10)
    contact_score: int = Field(ge=0, le=5)

    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)