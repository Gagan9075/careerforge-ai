from sqlalchemy.orm import Session

from app.models.user import User
from app.resume.model import Resume
from app.ai.model import ResumeAnalysis
from app.ats.model import ATSAnalysis


class DashboardService:

    def get_dashboard_data(
        self,
        user: User,
        db: Session,
    ) -> dict:

        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user.id)
            .first()
        )

        ats_analysis = None
        ai_analysis = None

        if resume:
            ats_analysis = (
                db.query(ATSAnalysis)
                .filter(ATSAnalysis.resume_id == resume.id)
                .first()
            )

            ai_analysis = (
                db.query(ResumeAnalysis)
                .filter(ResumeAnalysis.resume_id == resume.id)
                .first()
            )

        resume_data = None

        if resume:
            resume_data = {
                "id": str(resume.id),
                "title": resume.title,
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "location": resume.location,
                "summary": resume.summary,
            }

        ats_data = None

        if ats_analysis:
            ats_data = {
                "overall_score": ats_analysis.overall_score,
                "completeness_score": ats_analysis.completeness_score,
                "skills_score": ats_analysis.skills_score,
                "experience_score": ats_analysis.experience_score,
                "projects_score": ats_analysis.projects_score,
                "education_score": ats_analysis.education_score,
                "certifications_score": ats_analysis.certifications_score,
                "structure_score": ats_analysis.structure_score,
                "contact_score": ats_analysis.contact_score,
                "strengths": ats_analysis.strengths,
                "improvements": ats_analysis.improvements,
            }

        ai_data = None

        if ai_analysis:
            ai_data = {
                "overall_feedback": ai_analysis.overall_feedback,
                "strengths": ai_analysis.strengths,
                "missing_skills": ai_analysis.missing_skills,
                "recommended_skills": ai_analysis.recommended_skills,
                "project_feedback": ai_analysis.project_feedback,
                "improvement_suggestions": ai_analysis.improvement_suggestions,
            }

        return {
            "user": {
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            },
            "resume": resume_data,
            "ats_analysis": ats_data,
            "ai_analysis": ai_data,
        }
    