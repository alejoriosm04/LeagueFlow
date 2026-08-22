"""crear tabla login_attempts

Revision ID: c0bd195efdda
Revises: a7c8d9e0f1a2
Create Date: 2026-08-22 09:15:52.394606

Única migración de specs/017-bloqueo-login. Tabla nueva y aislada, sin claves
foráneas (deliberado: hay que contar identificadores inexistentes — FR-001).

Re-punteada al mergear: se generó contra `919f3bd57721`, pero para cuando se
abrió el PR ya estaban mezcladas la 013 (`8f42179847a1`) y la 014
(`a7c8d9e0f1a2`), que colgaban de la misma revisión. Dos migraciones con el
mismo `down_revision` dejan dos cabezas y rompen `alembic upgrade head`, así que
esta cuelga ahora de la cabeza ya mezclada (`AGENTS.md`, nota de migraciones en
paralelo). El contenido de la migración no cambia: `login_attempts` es una tabla
nueva y aislada, sin claves foráneas, que no colisiona con grupos ni tarjetas.

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
down_revision: Union[str, Sequence[str], None] = "a7c8d9e0f1a2"
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
