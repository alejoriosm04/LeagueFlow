"""crear tablas groups y group_memberships

Revision ID: 8f42179847a1
Revises: 919f3bd57721
Create Date: 2026-08-22 09:17:13.675813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f42179847a1'
down_revision: Union[str, Sequence[str], None] = '919f3bd57721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "groups",
        sa.Column("league_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_groups_unique_league_name",
        "groups",
        ["league_id", sa.literal_column("lower(trim(name))")],
        unique=True,
    )

    op.create_table(
        "group_memberships",
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_group_memberships_group", "group_memberships", ["group_id"], unique=False)
    op.create_index("uq_group_memberships_team", "group_memberships", ["team_id"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_group_memberships_team", table_name="group_memberships")
    op.drop_index("ix_group_memberships_group", table_name="group_memberships")
    op.drop_table("group_memberships")
    op.drop_index("ix_groups_unique_league_name", table_name="groups")
    op.drop_table("groups")
