"""add contact fields to resumes

Revision ID: 7327c0630ce4
Revises: add6998fcb1e
Create Date: 2026-09-29 13:00:57.994417

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7327c0630ce4"
down_revision: Union[str, Sequence[str], None] = "add6998fcb1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add contact fields to resumes."""
    op.add_column(
        "resumes",
        sa.Column("name", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "resumes",
        sa.Column("email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "resumes",
        sa.Column("phone", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "resumes",
        sa.Column("location", sa.String(length=150), nullable=True),
    )


def downgrade() -> None:
    """Remove contact fields from resumes."""
    op.drop_column("resumes", "location")
    op.drop_column("resumes", "phone")
    op.drop_column("resumes", "email")
    op.drop_column("resumes", "name")