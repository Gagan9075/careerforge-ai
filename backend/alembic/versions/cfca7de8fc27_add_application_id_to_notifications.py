"""add application id to notifications

Revision ID: cfca7de8fc27
Revises: bf6479340c65
Create Date: 2026-10-09 13:31:43.498448

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cfca7de8fc27"
down_revision: Union[str, Sequence[str], None] = "bf6479340c65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the application association to notifications."""

    op.add_column(
        "notifications",
        sa.Column("application_id", sa.UUID(), nullable=True),
    )

    op.create_index(
        "ix_notifications_application_id",
        "notifications",
        ["application_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_notifications_application_id_applications",
        "notifications",
        "applications",
        ["application_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Remove the application association from notifications."""

    op.drop_constraint(
        "fk_notifications_application_id_applications",
        "notifications",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_notifications_application_id",
        table_name="notifications",
    )

    op.drop_column(
        "notifications",
        "application_id",
    )