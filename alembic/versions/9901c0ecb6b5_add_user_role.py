"""add user role

Revision ID: 9901c0ecb6b5
Revises: 90e58f8a6dcc
Create Date: 2026-09-03 13:18:37.375634

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9901c0ecb6b5"
down_revision: Union[str, Sequence[str], None] = "90e58f8a6dcc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE users SET role = 'user' WHERE role IS NULL"
    )

    op.alter_column(
        "users",
        "role",
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "role",
    )