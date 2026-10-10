"""add external id to jobs

Revision ID: 9cc3486e806a
Revises: cfca7de8fc27
Create Date: 2026-10-10 14:09:44.525042

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9cc3486e806a"
down_revision: Union[str, Sequence[str], None] = "cfca7de8fc27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add external IDs and backfill IDs from existing Adzuna URLs."""

    # Add a nullable column so existing records remain valid.
    op.add_column(
        "jobs",
        sa.Column("external_id", sa.String(length=100), nullable=True),
    )

    # Extract stable Adzuna advertisement IDs from existing URLs.
    # Supports /land/ad/<id>, /details/<id>, and /ad/<id> patterns.
    op.execute(
        """
        UPDATE jobs
        SET external_id = COALESCE(
            NULLIF(
                split_part(
                    split_part(split_part(source_url, '?', 1), '/land/ad/', 2),
                    '/',
                    1
                ),
                ''
            ),
            NULLIF(
                split_part(
                    split_part(split_part(source_url, '?', 1), '/details/', 2),
                    '/',
                    1
                ),
                ''
            ),
            NULLIF(
                split_part(
                    split_part(split_part(source_url, '?', 1), '/ad/', 2),
                    '/',
                    1
                ),
                ''
            )
        )
        WHERE lower(source) = 'adzuna'
          AND external_id IS NULL
          AND (
              source_url LIKE '%/land/ad/%'
              OR source_url LIKE '%/details/%'
              OR source_url LIKE '%/ad/%'
          )
        """
    )


def downgrade() -> None:
    """Remove the external ID column."""

    op.drop_column("jobs", "external_id")