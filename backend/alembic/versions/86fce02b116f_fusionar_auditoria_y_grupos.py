"""fusionar auditoria y grupos

Revision ID: 86fce02b116f
Revises: 117e48f74b7c, 8f42179847a1
Create Date: 2026-08-22 00:00:00.000000

Migración de fusión, sin operaciones propias: 016 (`117e48f74b7c`, tabla
audit_logs) y 013 (`8f42179847a1`, tablas groups/group_memberships) se
ramificaron desde la misma cabeza al desarrollarse en paralelo, dejando dos
heads. Esta revisión las une en una sola línea.
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "86fce02b116f"
down_revision: str | Sequence[str] | None = ("117e48f74b7c", "a7c8d9e0f1a2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Fusión de heads: no aplica cambios de esquema propios."""
    pass


def downgrade() -> None:
    """Fusión de heads: no aplica cambios de esquema propios."""
    pass
