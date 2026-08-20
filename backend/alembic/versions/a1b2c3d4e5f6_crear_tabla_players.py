"""crear tabla players

Revision ID: a1b2c3d4e5f6
Revises: 36301f729230
Create Date: 2026-08-19 21:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "36301f729230"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "players",
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    # FR-003 / research.md §1: unicidad parcial — varios NULL permitidos.
    op.create_index(
        "ix_players_unique_team_number",
        "players",
        ["team_id", "number"],
        unique=True,
        postgresql_where=sa.text("number IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_players_unique_team_number",
        table_name="players",
        postgresql_where=sa.text("number IS NOT NULL"),
    )
    op.drop_table("players")
