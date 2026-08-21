"""indice matches liga status fecha

Revision ID: 5532b23cfb95
Revises: 020b6dc9a54e
Create Date: 2026-08-20 21:00:00.000000

specs/011-dashboard-liga/data-model.md §Migración.

Índice aditivo sobre `matches(league_id, status, scheduled_at)`: cubre el
filtro + orden que ya usan `MatchService.listar_partidos` (007) y
`listar_finalizados` (008), y que el dashboard (011) reutiliza tal cual sin
añadir consultas propias (research.md §4). No toca ninguna columna,
constraint ni índice existente — no hay índices funcionales involucrados
aquí, así que no aplica el gotcha de `AGENTS.md` sobre `lower(trim(...))`.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5532b23cfb95"
down_revision: str | Sequence[str] | None = "020b6dc9a54e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea el índice compuesto sobre matches."""
    op.create_index(
        "ix_matches_league_status_scheduled",
        "matches",
        ["league_id", "status", "scheduled_at"],
        unique=False,
    )


def downgrade() -> None:
    """Elimina el índice compuesto sobre matches."""
    op.drop_index("ix_matches_league_status_scheduled", table_name="matches")
