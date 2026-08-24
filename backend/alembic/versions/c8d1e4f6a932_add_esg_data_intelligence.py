"""Add the Sprint 8 ESG Data Intelligence evidence layer.

Revision ID: c8d1e4f6a932
Revises: b7c4e9f2a531
Create Date: 2026-08-23 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c8d1e4f6a932"
down_revision: str | None = "b7c4e9f2a531"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "esg_indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("pillar", sa.String(length=1), nullable=False, server_default="E"),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="external"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("pillar IN ('E', 'S', 'G')", name="ck_esg_indicators_pillar"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_esg_indicators_code", "esg_indicators", ["code"])
    op.create_index("ix_esg_indicators_category", "esg_indicators", ["category"])

    op.create_table(
        "indicator_values",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("source_reference", sa.String(length=1000), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("source_metadata", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="75"),
        sa.Column("freshness_score", sa.Float(), nullable=False, server_default="100"),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="85"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="80"),
        sa.CheckConstraint("quality_score BETWEEN 0 AND 100", name="ck_indicator_values_quality"),
        sa.CheckConstraint("freshness_score BETWEEN 0 AND 100", name="ck_indicator_values_freshness"),
        sa.CheckConstraint("relevance_score BETWEEN 0 AND 100", name="ck_indicator_values_relevance"),
        sa.CheckConstraint("confidence_score BETWEEN 0 AND 100", name="ck_indicator_values_confidence"),
        sa.ForeignKeyConstraint(["indicator_id"], ["esg_indicators.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, columns in (
        ("ix_indicator_values_indicator_id", ["indicator_id"]),
        ("ix_indicator_values_organization_id", ["organization_id"]),
        ("ix_indicator_values_site_id", ["site_id"]),
        ("ix_indicator_values_source", ["source"]),
        ("ix_indicator_values_observed_at", ["observed_at"]),
        ("ix_indicator_values_collected_at", ["collected_at"]),
    ):
        op.create_index(name, "indicator_values", columns)

    op.create_table(
        "materiality_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("materiality_assessment_id", sa.Integer(), nullable=False),
        sa.Column("indicator_value_id", sa.Integer(), nullable=False),
        sa.Column("relevance", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["materiality_assessment_id"], ["materiality_assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["indicator_value_id"], ["indicator_values.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("materiality_assessment_id", "indicator_value_id", name="uq_materiality_evidence_assessment_value"),
    )
    op.create_index("ix_materiality_evidence_materiality_assessment_id", "materiality_evidence", ["materiality_assessment_id"])
    op.create_index("ix_materiality_evidence_indicator_value_id", "materiality_evidence", ["indicator_value_id"])

    op.create_table(
        "provider_sync_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("data_category", sa.String(length=80), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, columns in (
        ("ix_provider_sync_logs_provider", ["provider"]),
        ("ix_provider_sync_logs_site_id", ["site_id"]),
        ("ix_provider_sync_logs_status", ["status"]),
        ("ix_provider_sync_logs_created_at", ["created_at"]),
    ):
        op.create_index(name, "provider_sync_logs", columns)


def downgrade() -> None:
    for name in (
        "ix_provider_sync_logs_created_at",
        "ix_provider_sync_logs_status",
        "ix_provider_sync_logs_site_id",
        "ix_provider_sync_logs_provider",
    ):
        op.drop_index(name, table_name="provider_sync_logs")
    op.drop_table("provider_sync_logs")
    op.drop_index("ix_materiality_evidence_indicator_value_id", table_name="materiality_evidence")
    op.drop_index("ix_materiality_evidence_materiality_assessment_id", table_name="materiality_evidence")
    op.drop_table("materiality_evidence")
    for name in (
        "ix_indicator_values_collected_at",
        "ix_indicator_values_observed_at",
        "ix_indicator_values_source",
        "ix_indicator_values_site_id",
        "ix_indicator_values_organization_id",
        "ix_indicator_values_indicator_id",
    ):
        op.drop_index(name, table_name="indicator_values")
    op.drop_table("indicator_values")
    op.drop_index("ix_esg_indicators_category", table_name="esg_indicators")
    op.drop_index("ix_esg_indicators_code", table_name="esg_indicators")
    op.drop_table("esg_indicators")
