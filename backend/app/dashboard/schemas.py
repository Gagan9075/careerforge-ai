from pydantic import BaseModel


class DashboardUserResponse(BaseModel):
    full_name: str
    email: str
    role: str


class DashboardResumeResponse(BaseModel):
    id: str
    title: str
    name: str | None
    email: str | None
    phone: str | None
    location: str | None
    summary: str | None


class DashboardATSResponse(BaseModel):
    overall_score: int
    completeness_score: int
    skills_score: int
    experience_score: int
    projects_score: int
    education_score: int
    certifications_score: int
    structure_score: int
    contact_score: int
    strengths: list[str]
    improvements: list[str]


class DashboardAIResponse(BaseModel):
    overall_feedback: str
    strengths: list[str]
    missing_skills: list[str]
    recommended_skills: list[str]
    project_feedback: list[str]
    improvement_suggestions: list[str]


class DashboardResponse(BaseModel):
    user: DashboardUserResponse
    resume: DashboardResumeResponse | None
    ats_analysis: DashboardATSResponse | None
    ai_analysis: DashboardAIResponse | None