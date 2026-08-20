"""registrar resultados y correcciones

Revision ID: d6e7f8a9b0c1
Revises: b2c3d4e5f6a7
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d6e7f8a9b0c1"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint("ck_matches_home_score_nonnegative", "matches", "home_score IS NULL OR home_score >= 0")
    op.create_check_constraint("ck_matches_away_score_nonnegative", "matches", "away_score IS NULL OR away_score >= 0")
    op.create_check_constraint(
        "ck_matches_status_scores_coherent",
        "matches",
        "(status = 'finished' AND home_score IS NOT NULL AND away_score IS NOT NULL) OR "
        "(status <> 'finished' AND home_score IS NULL AND away_score IS NULL)",
    )
    op.create_table(
        "result_correction_requests",
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("proposed_home_score", sa.Integer(), nullable=False),
        sa.Column("proposed_away_score", sa.Integer(), nullable=False),
        sa.Column("previous_home_score", sa.Integer(), nullable=False),
        sa.Column("previous_away_score", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("decided_by", sa.Uuid(), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("proposed_home_score >= 0", name="ck_corrections_proposed_home_nonnegative"),
        sa.CheckConstraint("proposed_away_score >= 0", name="ck_corrections_proposed_away_nonnegative"),
        sa.CheckConstraint("previous_home_score >= 0", name="ck_corrections_previous_home_nonnegative"),
        sa.CheckConstraint("previous_away_score >= 0", name="ck_corrections_previous_away_nonnegative"),
        sa.CheckConstraint("length(trim(reason)) > 0", name="ck_corrections_reason_nonempty"),
        sa.CheckConstraint(
            "(status = 'pending' AND decided_by IS NULL AND decided_at IS NULL AND decision_reason IS NULL) OR "
            "(status = 'approved' AND decided_by IS NOT NULL AND decided_at IS NOT NULL AND decision_reason IS NULL) OR "
            "(status = 'rejected' AND decided_by IS NOT NULL AND decided_at IS NOT NULL "
            "AND decision_reason IS NOT NULL AND length(trim(decision_reason)) > 0)",
            name="ck_corrections_resolution_coherent",
        ),
        sa.CheckConstraint("decided_by IS NULL OR decided_by <> requested_by", name="ck_corrections_separate_decider"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_corrections_match_created", "result_correction_requests", ["match_id", "created_at"])
    op.create_index(
        "ix_corrections_one_pending_per_match",
        "result_correction_requests",
        ["match_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index("ix_corrections_one_pending_per_match", table_name="result_correction_requests")
    op.drop_index("ix_corrections_match_created", table_name="result_correction_requests")
    op.drop_table("result_correction_requests")
    op.drop_constraint("ck_matches_status_scores_coherent", "matches", type_="check")
    op.drop_constraint("ck_matches_away_score_nonnegative", "matches", type_="check")
    op.drop_constraint("ck_matches_home_score_nonnegative", "matches", type_="check")
