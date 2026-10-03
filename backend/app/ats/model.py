import uuid

from sqlalchemy import ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ATSAnalysis(BaseModel):
    __tablename__ = "ats_analyses"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completeness_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skills_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    experience_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    projects_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    education_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    certifications_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    structure_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    contact_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    improvements: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )