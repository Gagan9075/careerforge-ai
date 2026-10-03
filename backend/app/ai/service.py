import json

from sqlalchemy.orm import Session

from app.ai.provider import AIProvider
from app.ai.schemas import ResumeAnalysisResponse
from app.models.user import User
from app.resume.model import Resume
from app.ai.model import ResumeAnalysis


class AIService:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def generate_response(self, prompt: str) -> str:
        return self.provider.generate(prompt)

    def analyze_resume(
        self,
        db: Session,
        resume: Resume,
        user: User,
    ) -> ResumeAnalysisResponse:

        existing_analysis = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.resume_id == resume.id
        ).first()

        if existing_analysis:
            return ResumeAnalysisResponse(
                overall_feedback=existing_analysis.overall_feedback,
                strengths=existing_analysis.strengths,
                missing_skills=existing_analysis.missing_skills,
                recommended_skills=existing_analysis.recommended_skills,
                project_feedback=existing_analysis.project_feedback,
                improvement_suggestions=existing_analysis.improvement_suggestions,
            )

        prompt = f"""
Analyze the following resume and return ONLY valid JSON.

Do not use markdown.
Do not use code fences.
Do not add explanations outside the JSON.

The JSON must have exactly these fields:

{{
  "overall_feedback": "string",
  "strengths": ["string"],
  "missing_skills": ["string"],
  "recommended_skills": ["string"],
  "project_feedback": ["string"],
  "improvement_suggestions": ["string"]
}}

Resume Title:
{resume.title}

Summary:
{resume.summary or "Not provided"}

Skills:
{resume.skills or "Not provided"}

Experience:
{resume.experience or "Not provided"}

Education:
{resume.education or "Not provided"}

Projects:
{resume.projects or "Not provided"}

Analyze the resume carefully and provide practical, specific feedback.
"""

        ai_response = self.provider.generate(prompt)

        try:
            analysis_data = json.loads(ai_response)

            analysis = ResumeAnalysis(
                resume_id=resume.id,
                overall_feedback=analysis_data["overall_feedback"],
                strengths=analysis_data["strengths"],
                missing_skills=analysis_data["missing_skills"],
                recommended_skills=analysis_data["recommended_skills"],
                project_feedback=analysis_data["project_feedback"],
                improvement_suggestions=analysis_data["improvement_suggestions"],
            )

            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            return ResumeAnalysisResponse.model_validate(analysis_data)

        except (json.JSONDecodeError, KeyError, ValueError):

            return ResumeAnalysisResponse(
                overall_feedback=ai_response,
                strengths=[],
                missing_skills=[],
                recommended_skills=[],
                project_feedback=[],
                improvement_suggestions=[],
            )