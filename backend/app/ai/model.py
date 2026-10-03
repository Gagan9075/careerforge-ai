import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ResumeAnalysis(BaseModel):
    __tablename__ = "resume_analyses"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    overall_feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    missing_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    recommended_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    project_feedback: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    improvement_suggestions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )