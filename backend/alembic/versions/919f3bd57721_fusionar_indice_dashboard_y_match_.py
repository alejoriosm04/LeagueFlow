"""fusionar indice dashboard y match_lineups

Revision ID: 919f3bd57721
Revises: 5532b23cfb95, f3a4b5c6d7e8
Create Date: 2026-08-20 23:03:23.565347

Migración de fusión, sin operaciones propias: 011 (`5532b23cfb95`, índice de
`matches`) y 010 (`f3a4b5c6d7e8`, tabla `match_lineups`) se ramificaron desde
la misma cabeza (`020b6dc9a54e`) al desarrollarse en paralelo, dejando dos
heads. Esta revisión las une en una sola línea, igual que ya hizo GitHub con
el merge de código en `backend/src/statistics/`.
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "919f3bd57721"
down_revision: str | Sequence[str] | None = ("5532b23cfb95", "f3a4b5c6d7e8")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Fusión de heads: no aplica cambios de esquema propios."""
    pass


def downgrade() -> None:
    """Fusión de heads: no aplica cambios de esquema propios."""
    pass
