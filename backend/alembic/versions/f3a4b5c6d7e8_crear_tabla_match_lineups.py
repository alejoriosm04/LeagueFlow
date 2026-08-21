"""crear tabla match_lineups

Revision ID: f3a4b5c6d7e8
Revises: 020b6dc9a54e
Create Date: 2026-08-20 17:05:00.000000

specs/010-alineaciones-estadisticas/data-model.md §MatchLineup.

NOTA (AGENTS.md, sección de migraciones): si se regenera este archivo con
`alembic revision --autogenerate`, revisar el diff y eliminar cualquier
`drop_index`/`create_index` espurio sobre `ix_leagues_unique_name_season` o
`ix_teams_unique_league_name` — son índices funcionales de specs anteriores
que Alembic detecta como "cambiados" sin que nadie los haya tocado. Esta
migración escrita a mano no crea ni toca ningún índice fuera de
`match_lineups`.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3a4b5c6d7e8"
down_revision: str | Sequence[str] | None = "020b6dc9a54e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea la tabla de alineaciones de partido."""
    op.create_table(
        "match_lineups",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_match_lineups_match_player",
        "match_lineups",
        ["match_id", "player_id"],
        unique=True,
    )
    op.create_index(
        "ix_match_lineups_match_team", "match_lineups", ["match_id", "team_id"], unique=False
    )
    op.create_index("ix_match_lineups_player", "match_lineups", ["player_id"], unique=False)


def downgrade() -> None:
    """Elimina la tabla de alineaciones de partido."""
    op.drop_index("ix_match_lineups_player", table_name="match_lineups")
    op.drop_index("ix_match_lineups_match_team", table_name="match_lineups")
    op.drop_index("uq_match_lineups_match_player", table_name="match_lineups")
    op.drop_table("match_lineups")
