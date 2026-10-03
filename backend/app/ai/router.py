from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.ai.model import ResumeAnalysis
from app.ai.schemas import ResumeAnalysisRequest, ResumeAnalysisResponse
from app.ai.service import AIService
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.resume.model import Resume


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


@router.post(
    "/analyze-resume",
    response_model=ResumeAnalysisResponse,
)
def analyze_resume(
    request: ResumeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, request.resume_id)

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resume",
        )

    ai_service = AIService(get_ai_provider())

    return ai_service.analyze_resume(
        db=db,
        resume=resume,
        user=current_user,
    )

@router.get("/resume-analysis/me", response_model=ResumeAnalysisResponse)
def get_my_resume_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.scalar(
        select(Resume).where(Resume.user_id == current_user.id)
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    analysis = db.scalar(
        select(ResumeAnalysis).where(
            ResumeAnalysis.resume_id == resume.id
        )
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found",
        )

    return ResumeAnalysisResponse(
        overall_feedback=analysis.overall_feedback,
        strengths=analysis.strengths,
        missing_skills=analysis.missing_skills,
        recommended_skills=analysis.recommended_skills,
        project_feedback=analysis.project_feedback,
        improvement_suggestions=analysis.improvement_suggestions,
    )