"""Add the Sprint 7 Materiality Engine domain.

Revision ID: b7c4e9f2a531
Revises: 8e6f2a10d9c1
Create Date: 2026-08-22 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c4e9f2a531"
down_revision: str | None = "8e6f2a10d9c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "materiality_assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("reporting_year", sa.Integer(), nullable=False),
        sa.Column("impact_score", sa.Float(), nullable=True),
        sa.Column("financial_score", sa.Float(), nullable=True),
        sa.Column("stakeholder_score", sa.Float(), nullable=True),
        sa.Column("materiality_score", sa.Float(), nullable=True),
        sa.Column("priority_level", sa.String(length=12), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("reporting_year BETWEEN 2000 AND 2100", name="ck_materiality_reporting_year"),
        sa.CheckConstraint(
            "status IN ('draft', 'in_review', 'completed')", name="ck_materiality_assessments_status"
        ),
        sa.CheckConstraint(
            "priority_level IS NULL OR priority_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_materiality_assessments_priority",
        ),
        sa.CheckConstraint(
            "impact_score IS NULL OR impact_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_impact_score",
        ),
        sa.CheckConstraint(
            "financial_score IS NULL OR financial_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_financial_score",
        ),
        sa.CheckConstraint(
            "stakeholder_score IS NULL OR stakeholder_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_stakeholder_score",
        ),
        sa.CheckConstraint(
            "materiality_score IS NULL OR materiality_score BETWEEN 0 AND 100",
            name="ck_materiality_assessments_score",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "topic_id",
            "reporting_year",
            name="uq_materiality_assessments_organization_topic_year",
        ),
    )
    op.create_index("ix_materiality_assessments_organization_id", "materiality_assessments", ["organization_id"])
    op.create_index("ix_materiality_assessments_topic_id", "materiality_assessments", ["topic_id"])
    op.create_index("ix_materiality_assessments_reporting_year", "materiality_assessments", ["reporting_year"])
    op.create_index("ix_materiality_assessments_materiality_score", "materiality_assessments", ["materiality_score"])
    op.create_index("ix_materiality_assessments_priority_level", "materiality_assessments", ["priority_level"])

    op.create_table(
        "impact_assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("materiality_assessment_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("scope", sa.Integer(), nullable=False),
        sa.Column("likelihood", sa.Integer(), nullable=False),
        sa.Column("remediability", sa.Integer(), nullable=False),
        sa.CheckConstraint("severity BETWEEN 1 AND 5", name="ck_impact_assessments_severity"),
        sa.CheckConstraint("scope BETWEEN 1 AND 5", name="ck_impact_assessments_scope"),
        sa.CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_impact_assessments_likelihood"),
        sa.CheckConstraint("remediability BETWEEN 1 AND 5", name="ck_impact_assessments_remediability"),
        sa.ForeignKeyConstraint(["materiality_assessment_id"], ["materiality_assessments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("materiality_assessment_id"),
    )
    op.create_table(
        "financial_assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("materiality_assessment_id", sa.Integer(), nullable=False),
        sa.Column("revenue_impact", sa.Integer(), nullable=False),
        sa.Column("cost_impact", sa.Integer(), nullable=False),
        sa.Column("asset_impact", sa.Integer(), nullable=False),
        sa.Column("financing_impact", sa.Integer(), nullable=False),
        sa.Column("regulatory_impact", sa.Integer(), nullable=False),
        sa.CheckConstraint("revenue_impact BETWEEN 1 AND 5", name="ck_financial_assessments_revenue"),
        sa.CheckConstraint("cost_impact BETWEEN 1 AND 5", name="ck_financial_assessments_cost"),
        sa.CheckConstraint("asset_impact BETWEEN 1 AND 5", name="ck_financial_assessments_asset"),
        sa.CheckConstraint("financing_impact BETWEEN 1 AND 5", name="ck_financial_assessments_financing"),
        sa.CheckConstraint("regulatory_impact BETWEEN 1 AND 5", name="ck_financial_assessments_regulatory"),
        sa.ForeignKeyConstraint(["materiality_assessment_id"], ["materiality_assessments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("materiality_assessment_id"),
    )
    op.create_table(
        "stakeholder_assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("materiality_assessment_id", sa.Integer(), nullable=False),
        sa.Column("stakeholder_id", sa.Integer(), nullable=False),
        sa.Column("relevance", sa.Integer(), nullable=False),
        sa.Column("concern_level", sa.Integer(), nullable=False),
        sa.Column("influence", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("relevance BETWEEN 1 AND 5", name="ck_stakeholder_assessments_relevance"),
        sa.CheckConstraint("concern_level BETWEEN 1 AND 5", name="ck_stakeholder_assessments_concern"),
        sa.CheckConstraint("influence BETWEEN 1 AND 5", name="ck_stakeholder_assessments_influence"),
        sa.ForeignKeyConstraint(["materiality_assessment_id"], ["materiality_assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["stakeholder_id"], ["stakeholders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "materiality_assessment_id",
            "stakeholder_id",
            name="uq_stakeholder_assessments_assessment_stakeholder",
        ),
    )
    op.create_index("ix_stakeholder_assessments_materiality_assessment_id", "stakeholder_assessments", ["materiality_assessment_id"])
    op.create_index("ix_stakeholder_assessments_stakeholder_id", "stakeholder_assessments", ["stakeholder_id"])

    op.create_table(
        "assessment_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("materiality_assessment_id", sa.Integer(), nullable=False),
        sa.Column("evidence_type", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reference", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "evidence_type IN ('manual', 'internal_data', 'external_data', 'document', 'stakeholder')",
            name="ck_assessment_evidence_type",
        ),
        sa.ForeignKeyConstraint(["materiality_assessment_id"], ["materiality_assessments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessment_evidence_materiality_assessment_id", "assessment_evidence", ["materiality_assessment_id"])


def downgrade() -> None:
    op.drop_index("ix_assessment_evidence_materiality_assessment_id", table_name="assessment_evidence")
    op.drop_table("assessment_evidence")
    op.drop_index("ix_stakeholder_assessments_stakeholder_id", table_name="stakeholder_assessments")
    op.drop_index("ix_stakeholder_assessments_materiality_assessment_id", table_name="stakeholder_assessments")
    op.drop_table("stakeholder_assessments")
    op.drop_table("financial_assessments")
    op.drop_table("impact_assessments")
    op.drop_index("ix_materiality_assessments_priority_level", table_name="materiality_assessments")
    op.drop_index("ix_materiality_assessments_materiality_score", table_name="materiality_assessments")
    op.drop_index("ix_materiality_assessments_reporting_year", table_name="materiality_assessments")
    op.drop_index("ix_materiality_assessments_topic_id", table_name="materiality_assessments")
    op.drop_index("ix_materiality_assessments_organization_id", table_name="materiality_assessments")
    op.drop_table("materiality_assessments")
