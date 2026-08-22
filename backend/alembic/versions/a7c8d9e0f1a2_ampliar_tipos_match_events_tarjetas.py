"""ampliar tipos match_events para tarjetas — spec 014

Revision ID: a7c8d9e0f1a2
Revises: 919f3bd57721
Create Date: 2026-08-22

specs/014-tarjetas-sanciones/data-model.md — solo reemplaza el CHECK de tipos.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7c8d9e0f1a2"
down_revision: str | Sequence[str] | None = "919f3bd57721"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_match_events_type_supported", "match_events", type_="check")
    op.create_check_constraint(
        "ck_match_events_type_supported",
        "match_events",
        "type IN ('GOAL', 'YELLOW_CARD', 'RED_CARD')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_match_events_type_supported", "match_events", type_="check")
    op.create_check_constraint(
        "ck_match_events_type_supported",
        "match_events",
        "type IN ('GOAL')",
    )
