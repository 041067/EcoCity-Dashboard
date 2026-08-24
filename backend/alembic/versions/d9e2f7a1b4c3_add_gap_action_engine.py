"""Add the Sprint 9 Gap & Action Engine.

Revision ID: d9e2f7a1b4c3
Revises: c8d1e4f6a932
Create Date: 2026-08-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d9e2f7a1b4c3"
down_revision: str | None = "c8d1e4f6a932"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _index(name: str, table: str, column: str) -> None:
    op.create_index(name, table, [column])


def upgrade() -> None:
    op.add_column(
        "esg_indicators",
        sa.Column("direction", sa.String(length=24), nullable=False, server_default="higher_is_better"),
    )
    op.execute(
        "UPDATE esg_indicators SET direction = 'lower_is_better' "
        "WHERE code IN ('AIR_PM25', 'AIR_PM10', 'AIR_NO2', 'AIR_O3', 'AIR_SO2', 'AIR_CO', "
        "'FOREST_FIRE_ALERTS', 'TERRITORY_DEFORESTATION_ALERTS', 'CLIMATE_HEAT_RISK', "
        "'WATER_DROUGHT_RISK', 'CLIMATE_FLOOD_RISK', 'CLIMATE_WIND_RISK', 'WATER_STRESS_SIGNAL')"
    )

    op.create_table(
        "esg_targets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("baseline_value", sa.Float(), nullable=False),
        sa.Column("baseline_year", sa.Integer(), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("target_year", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("baseline_year BETWEEN 2000 AND 2100", name="ck_esg_targets_baseline_year"),
        sa.CheckConstraint("target_year BETWEEN 2000 AND 2100", name="ck_esg_targets_target_year"),
        sa.CheckConstraint("target_year > baseline_year", name="ck_esg_targets_year_order"),
        sa.CheckConstraint("status IN ('planned', 'active', 'achieved', 'cancelled')", name="ck_esg_targets_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["indicator_id"], ["esg_indicators.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("organization_id", "site_id", "topic_id", "indicator_id", "status"):
        _index(f"ix_esg_targets_{column}", "esg_targets", column)

    op.create_table(
        "esg_gaps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("gap_type", sa.String(length=80), nullable=False, server_default="target_variance"),
        sa.Column("severity", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False, server_default="open"),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("gap_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name="ck_esg_gaps_severity"),
        sa.CheckConstraint("status IN ('open', 'resolved')", name="ck_esg_gaps_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["indicator_id"], ["esg_indicators.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_id"], ["esg_targets.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assessment_id"], ["materiality_assessments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "fingerprint", name="uq_esg_gaps_organization_fingerprint"),
    )
    for column in ("organization_id", "site_id", "topic_id", "indicator_id", "target_id", "assessment_id", "severity", "status"):
        _index(f"ix_esg_gaps_{column}", "esg_gaps", column)

    op.create_table(
        "esg_risks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("indicator_value_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("risk_type", sa.String(length=80), nullable=False),
        sa.Column("likelihood", sa.Integer(), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=12), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_esg_risks_likelihood"),
        sa.CheckConstraint("impact BETWEEN 1 AND 5", name="ck_esg_risks_impact"),
        sa.CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_esg_risks_score"),
        sa.CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name="ck_esg_risks_level"),
        sa.CheckConstraint("status IN ('open', 'mitigating', 'resolved')", name="ck_esg_risks_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["indicator_value_id"], ["indicator_values.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "fingerprint", name="uq_esg_risks_organization_fingerprint"),
    )
    for column in ("organization_id", "site_id", "topic_id", "indicator_value_id", "risk_score", "risk_level", "status"):
        _index(f"ix_esg_risks_{column}", "esg_risks", column)

    op.create_table(
        "esg_opportunities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=True),
        sa.Column("indicator_value_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("opportunity_type", sa.String(length=80), nullable=False),
        sa.Column("potential_impact", sa.Integer(), nullable=False),
        sa.Column("feasibility", sa.Integer(), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=False),
        sa.Column("priority", sa.String(length=12), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_reference", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("potential_impact BETWEEN 1 AND 5", name="ck_esg_opportunities_impact"),
        sa.CheckConstraint("feasibility BETWEEN 1 AND 5", name="ck_esg_opportunities_feasibility"),
        sa.CheckConstraint("opportunity_score BETWEEN 0 AND 100", name="ck_esg_opportunities_score"),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_esg_opportunities_priority"),
        sa.CheckConstraint("status IN ('open', 'in_progress', 'realized', 'dismissed')", name="ck_esg_opportunities_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["indicator_id"], ["esg_indicators.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["indicator_value_id"], ["indicator_values.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "fingerprint", name="uq_esg_opportunities_organization_fingerprint"),
    )
    for column in ("organization_id", "site_id", "topic_id", "indicator_id", "indicator_value_id", "opportunity_score", "priority", "status"):
        _index(f"ix_esg_opportunities_{column}", "esg_opportunities", column)

    op.create_table(
        "action_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False), sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("topic_id", sa.Integer(), nullable=False), sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("gap_id", sa.Integer(), nullable=True), sa.Column("risk_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=240), nullable=False), sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(length=12), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="planned"),
        sa.Column("responsible_area", sa.String(length=160), nullable=True), sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("progress_percentage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_action_plans_priority"),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'blocked', 'completed', 'cancelled')", name="ck_action_plans_status"),
        sa.CheckConstraint("progress_percentage BETWEEN 0 AND 100", name="ck_action_plans_progress"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_id"], ["esg_targets.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["gap_id"], ["esg_gaps.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["risk_id"], ["esg_risks.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"),
    )
    for column in ("organization_id", "site_id", "topic_id", "target_id", "gap_id", "risk_id", "priority", "status", "due_date"):
        _index(f"ix_action_plans_{column}", "action_plans", column)

    op.create_table(
        "action_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("action_plan_id", sa.Integer(), nullable=False), sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True), sa.Column("status", sa.String(length=16), nullable=False, server_default="planned"),
        sa.Column("due_date", sa.Date(), nullable=True), sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'blocked', 'completed', 'cancelled')", name="ck_action_tasks_status"),
        sa.ForeignKeyConstraint(["action_plan_id"], ["action_plans.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"),
    )
    for column in ("action_plan_id", "status", "due_date"):
        _index(f"ix_action_tasks_{column}", "action_tasks", column)

    op.create_table(
        "audit_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False), sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False, server_default="system"), sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True), sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True), sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=False, server_default="api"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"),
    )
    for column in ("organization_id", "entity_type", "entity_id", "action", "created_at"):
        _index(f"ix_audit_entries_{column}", "audit_entries", column)


def downgrade() -> None:
    for table, columns in (
        ("audit_entries", ("created_at", "action", "entity_id", "entity_type", "organization_id")),
        ("action_tasks", ("due_date", "status", "action_plan_id")),
        ("action_plans", ("due_date", "status", "priority", "risk_id", "gap_id", "target_id", "topic_id", "site_id", "organization_id")),
        ("esg_opportunities", ("status", "priority", "opportunity_score", "indicator_value_id", "indicator_id", "topic_id", "site_id", "organization_id")),
        ("esg_risks", ("status", "risk_level", "risk_score", "indicator_value_id", "topic_id", "site_id", "organization_id")),
        ("esg_gaps", ("status", "severity", "assessment_id", "target_id", "indicator_id", "topic_id", "site_id", "organization_id")),
        ("esg_targets", ("status", "indicator_id", "topic_id", "site_id", "organization_id")),
    ):
        for column in columns:
            op.drop_index(f"ix_{table}_{column}", table_name=table)
        op.drop_table(table)
    op.drop_column("esg_indicators", "direction")
