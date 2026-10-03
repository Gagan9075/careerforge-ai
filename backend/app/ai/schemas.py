from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    resume_id: str


class ResumeAnalysisResponse(BaseModel):
    overall_feedback: str

    strengths: list[str] = Field(default_factory=list)

    missing_skills: list[str] = Field(default_factory=list)

    recommended_skills: list[str] = Field(default_factory=list)

    project_feedback: list[str] = Field(default_factory=list)

    improvement_suggestions: list[str] = Field(default_factory=list)