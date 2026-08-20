"""crear tabla match_events

Revision ID: 020b6dc9a54e
Revises: d6e7f8a9b0c1
Create Date: 2026-08-20 16:20:39.931050

specs/009-registrar-goles/data-model.md §MatchEvent.

NOTA: el autogenerate añadió además un DROP/CREATE de
`ix_leagues_unique_name_season` e `ix_teams_unique_league_name`. Son espurios:
PostgreSQL normaliza `trim(x)` como `TRIM(BOTH FROM x)` en su catálogo, así que
Alembic los ve distintos aunque nadie los haya tocado (AGENTS.md, sección de
migraciones). Se eliminaron a mano: esta HU no toca índices de otras specs
(Principio IV).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "020b6dc9a54e"
down_revision: str | Sequence[str] | None = "d6e7f8a9b0c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea la tabla de eventos de partido."""
    op.create_table(
        "match_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("minute >= 0", name="ck_match_events_minute_nonnegative"),
        sa.CheckConstraint("type IN ('GOAL')", name="ck_match_events_type_supported"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_match_events_match_minute", "match_events", ["match_id", "minute"], unique=False
    )


def downgrade() -> None:
    """Elimina la tabla de eventos de partido."""
    op.drop_index("ix_match_events_match_minute", table_name="match_events")
    op.drop_table("match_events")
