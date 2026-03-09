"""update users, hotels, bookings models

Revision ID: 5a3242853da6
Revises: 0280654b559d
Create Date: 2026-02-10 16:08:02.107975

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5a3242853da6"
down_revision: Union[str, Sequence[str], None] = "0280654b559d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings", sa.Column("rate", sa.String(), server_default="0", nullable=False)
    )
    op.add_column(
        "hotels", sa.Column("rating", sa.Float(), server_default="0", nullable=False)
    )
    op.add_column(
        "users", sa.Column("status", sa.String(), server_default="0", nullable=False)
    )


def downgrade() -> None:
    op.drop_column("users", "status")
    op.drop_column("hotels", "rating")
    op.drop_column("bookings", "rate")
