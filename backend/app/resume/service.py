from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.resume.model import Resume
from app.resume.schemas import ResumeCreate, ResumeUpdate


def get_resume(db: Session, user: User) -> Resume | None:
    return db.scalar(
        select(Resume).where(Resume.user_id == user.id)
    )


def create_resume(
    db: Session,
    user: User,
    resume_data: ResumeCreate,
) -> Resume:

    existing_resume = get_resume(db, user)

    if existing_resume:
        raise ValueError("Resume already exists")

    resume = Resume(
        user_id=user.id,
        title=resume_data.title,
        summary=resume_data.summary,
        skills=resume_data.skills,
        experience=resume_data.experience,
        education=resume_data.education,
        projects=resume_data.projects,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def update_resume(
    db: Session,
    user: User,
    resume_data: ResumeUpdate,
) -> Resume | None:

    resume = get_resume(db, user)

    if not resume:
        return None

    resume.title = resume_data.title
    resume.summary = resume_data.summary
    resume.skills = resume_data.skills
    resume.experience = resume_data.experience
    resume.education = resume_data.education
    resume.projects = resume_data.projects

    db.commit()
    db.refresh(resume)

    return resume