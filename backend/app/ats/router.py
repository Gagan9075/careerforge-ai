from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.resume.model import Resume

from app.ats.model import ATSAnalysis
from app.ats.schemas import ATSScoreResponse
from app.ats.service import ATSService


router = APIRouter(
    prefix="/api/ats",
    tags=["ATS"],
)


@router.post("/analyze", response_model=ATSScoreResponse)
def analyze_my_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload a resume first.",
        )

    ats_service = ATSService()
    result = ats_service.analyze_resume(resume)

    existing_analysis = (
        db.query(ATSAnalysis)
        .filter(ATSAnalysis.resume_id == resume.id)
        .first()
    )

    if existing_analysis:
        existing_analysis.overall_score = result["overall_score"]
        existing_analysis.completeness_score = result["completeness_score"]
        existing_analysis.skills_score = result["skills_score"]
        existing_analysis.experience_score = result["experience_score"]
        existing_analysis.projects_score = result["projects_score"]
        existing_analysis.education_score = result["education_score"]
        existing_analysis.certifications_score = result["certifications_score"]
        existing_analysis.structure_score = result["structure_score"]
        existing_analysis.contact_score = result["contact_score"]
        existing_analysis.strengths = result["strengths"]
        existing_analysis.improvements = result["improvements"]

        analysis = existing_analysis

    else:
        analysis = ATSAnalysis(
            resume_id=resume.id,
            overall_score=result["overall_score"],
            completeness_score=result["completeness_score"],
            skills_score=result["skills_score"],
            experience_score=result["experience_score"],
            projects_score=result["projects_score"],
            education_score=result["education_score"],
            certifications_score=result["certifications_score"],
            structure_score=result["structure_score"],
            contact_score=result["contact_score"],
            strengths=result["strengths"],
            improvements=result["improvements"],
        )

        db.add(analysis)

    db.commit()

    return result

@router.get("/me", response_model=ATSScoreResponse)
def get_my_ats_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload a resume first.",
        )

    analysis = (
        db.query(ATSAnalysis)
        .filter(ATSAnalysis.resume_id == resume.id)
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="ATS analysis not found. Please analyze your resume first.",
        )

    return analysis