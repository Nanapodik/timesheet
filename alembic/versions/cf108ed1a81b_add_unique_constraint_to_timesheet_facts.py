"""add unique constraint to timesheet facts

Revision ID: cf108ed1a81b
Revises: ca0d1f243e12
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cf108ed1a81b"
down_revision: Union[str, Sequence[str], None] = "ca0d1f243e12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_unique_constraint(
        "uq_timesheet_fact_employee_date",
        "timesheet_facts",
        ["employee_id", "work_date"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_timesheet_fact_employee_date",
        "timesheet_facts",
        type_="unique",
    )