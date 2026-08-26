"""Add Sprint 10 ESG AI Copilot persistence.

Revision ID: e4f5a6b7c8d9
Revises: d9e2f7a1b4c3
Create Date: 2026-08-26 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: str | None = "d9e2f7a1b4c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "esg_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("report_type", sa.String(length=24), nullable=False),
        sa.Column("reporting_year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="completed"),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("data_sufficiency", sa.JSON(), nullable=False),
        sa.Column("context_hash", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "report_type IN ('executive', 'materiality', 'risk', 'progress', 'full_esg')",
            name="ck_esg_reports_type",
        ),
        sa.CheckConstraint("status IN ('completed', 'failed')", name="ck_esg_reports_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_esg_reports_organization_id", "esg_reports", ["organization_id"])
    op.create_index("ix_esg_reports_report_type", "esg_reports", ["report_type"])
    op.create_index("ix_esg_reports_reporting_year", "esg_reports", ["reporting_year"])
    op.create_index("ix_esg_reports_context_hash", "esg_reports", ["context_hash"])
    op.create_index("ix_esg_reports_generated_at", "esg_reports", ["generated_at"])

    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("expected_impact", sa.Text(), nullable=False),
        sa.Column("time_horizon", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=12), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("context_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("action_plan_id", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_ai_recommendations_priority"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'dismissed', 'converted')",
            name="ck_ai_recommendations_status",
        ),
        sa.CheckConstraint(
            "time_horizon IN ('immediate', 'short_term', 'medium_term', 'long_term')",
            name="ck_ai_recommendations_horizon",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["action_plan_id"], ["action_plans.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_recommendations_organization_id", "ai_recommendations", ["organization_id"])
    op.create_index("ix_ai_recommendations_topic_id", "ai_recommendations", ["topic_id"])
    op.create_index("ix_ai_recommendations_priority", "ai_recommendations", ["priority"])
    op.create_index("ix_ai_recommendations_context_hash", "ai_recommendations", ["context_hash"])
    op.create_index("ix_ai_recommendations_status", "ai_recommendations", ["status"])
    op.create_index("ix_ai_recommendations_generated_at", "ai_recommendations", ["generated_at"])

    op.create_table(
        "ai_usage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("operation", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('success', 'failure', 'cache_hit', 'rate_limited')", name="ck_ai_usage_status"
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_usage_organization_id", "ai_usage", ["organization_id"])
    op.create_index("ix_ai_usage_operation", "ai_usage", ["operation"])
    op.create_index("ix_ai_usage_status", "ai_usage", ["status"])
    op.create_index("ix_ai_usage_created_at", "ai_usage", ["created_at"])


def downgrade() -> None:
    op.drop_table("ai_usage")
    op.drop_table("ai_recommendations")
    op.drop_table("esg_reports")
