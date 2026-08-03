"""add uv_index to sensor_readings and alerts table

Revision ID: 6125febb329f
Revises: 0d52082d1168
Create Date: 2026-08-01 16:33:43.671331
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '6125febb329f'
down_revision: str | None = '0d52082d1168'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sensor_readings",
        sa.Column("uv_index", sa.Float(), nullable=False, server_default="0.0"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_city_id", "alerts", ["city_id"])


def downgrade() -> None:
    op.drop_index("ix_alerts_city_id", table_name="alerts")
    op.drop_table("alerts")
    op.drop_column("sensor_readings", "uv_index")
