"""crear tabla login_attempts

Revision ID: c0bd195efdda
Revises: 86fce02b116f
Create Date: 2026-08-22 09:15:52.394606

Única migración de specs/017-bloqueo-login. Tabla nueva y aislada, sin claves
foráneas (deliberado: hay que contar identificadores inexistentes — FR-001).

Re-punteada dos veces al mergear, por el bloque de trabajo paralelo. Se generó
contra `919f3bd57721`; después se mezclaron la 013 (`8f42179847a1`) y la 014
(`a7c8d9e0f1a2`), y más tarde la 016, que además de `117e48f74b7c` (audit_logs)
trajo una migración de FUSIÓN, `86fce02b116f`, que une auditoría con grupos.

Esa fusión convirtió `a7c8d9e0f1a2` en un nodo interno, así que colgar de él
volvía a dejar dos cabezas. Esta migración cuelga ahora de `86fce02b116f`, la
cabeza real de `main` (`AGENTS.md`, nota de migraciones en paralelo).

Como 017 es la última del bloque, aquí NO hace falta otra fusión: basta con
encadenar. El contenido no cambia — `login_attempts` es una tabla nueva y
aislada, sin claves foráneas, que no colisiona con grupos, tarjetas ni
auditoría.

`--autogenerate` propuso además recrear `ix_leagues_unique_name_season` y
`ix_teams_unique_league_name`: es el falso positivo de índices funcionales que
documenta AGENTS.md (PostgreSQL normaliza `trim(x)` como `TRIM(BOTH FROM x)` en
su catálogo). Esos índices NO han cambiado, así que sus operaciones se
eliminaron del diff a mano (Principio IV).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c0bd195efdda"
down_revision: Union[str, Sequence[str], None] = "86fce02b116f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "login_attempts",
        sa.Column("username_normalizado", sa.String(length=60), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_attempt_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # UNIQUE: además de integridad, es el `ON CONFLICT target` del UPSERT
    # atómico que hace el conteo consistente ante intentos simultáneos.
    op.create_index(
        op.f("ix_login_attempts_username_normalizado"),
        "login_attempts",
        ["username_normalizado"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_login_attempts_username_normalizado"), table_name="login_attempts")
    op.drop_table("login_attempts")
