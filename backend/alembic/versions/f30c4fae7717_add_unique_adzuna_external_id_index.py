"""add unique Adzuna external ID index

Revision ID: f30c4fae7717
Revises: 9cc3486e806a
Create Date: 2026-10-10 14:49:31.668256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f30c4fae7717'
down_revision: Union[str, Sequence[str], None] = '9cc3486e806a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Prevent duplicate Adzuna advertisement IDs."""

    op.create_index(
        "uq_jobs_adzuna_external_id",
        "jobs",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text(
            "lower(source) = 'adzuna' AND external_id IS NOT NULL"
        ),
    )


def downgrade() -> None:
    """Remove the Adzuna external ID uniqueness constraint."""

    op.drop_index(
        "uq_jobs_adzuna_external_id",
        table_name="jobs",
    )
