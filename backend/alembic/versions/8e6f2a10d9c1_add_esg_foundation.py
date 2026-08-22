"""Add ESG foundation domain.

Revision ID: 8e6f2a10d9c1
Revises: 6125febb329f
Create Date: 2026-08-22 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8e6f2a10d9c1"
down_revision: str | None = "6125febb329f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # This migration is intentionally additive: existing environmental tables remain unchanged.
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("organization_type", sa.String(length=30), nullable=False),
        sa.Column("industry_sector", sa.String(length=120), nullable=True),
        sa.Column("document", sa.String(length=40), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False, server_default="Brasil"),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "organization_type IN ('company', 'municipality', 'public_agency', 'university', 'other')",
            name="ck_organizations_type",
        ),
        sa.CheckConstraint("employee_count IS NULL OR employee_count >= 0", name="ck_organizations_employee_count"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document"),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])

    op.create_table(
        "esg_topics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("pillar", sa.String(length=1), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("pillar IN ('E', 'S', 'G')", name="ck_esg_topics_pillar"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_esg_topics_pillar", "esg_topics", ["pillar"])

    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("site_type", sa.String(length=30), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("city_id", sa.Integer(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("area_m2", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "site_type IN ('headquarters', 'factory', 'warehouse', 'office', 'municipal_region', 'other')",
            name="ck_sites_type",
        ),
        sa.CheckConstraint("employee_count IS NULL OR employee_count >= 0", name="ck_sites_employee_count"),
        sa.CheckConstraint("area_m2 IS NULL OR area_m2 >= 0", name="ck_sites_area_m2"),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sites_organization_id", "sites", ["organization_id"])
    op.create_index("ix_sites_city_id", "sites", ["city_id"])

    op.create_table(
        "esg_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("reporting_year", sa.Integer(), nullable=False),
        sa.Column("environmental_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("social_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("governance_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sustainability_strategy", sa.Text(), nullable=True),
        sa.Column("esg_maturity_level", sa.String(length=20), nullable=False, server_default="initial"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "esg_maturity_level IN ('initial', 'developing', 'structured', 'advanced')",
            name="ck_esg_profiles_maturity",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_table(
        "stakeholders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("stakeholder_type", sa.String(length=30), nullable=False),
        sa.Column("influence_level", sa.Integer(), nullable=False),
        sa.Column("impact_level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "stakeholder_type IN ('employees', 'customers', 'suppliers', 'investors', 'government', "
            "'community', 'environment', 'partners', 'other')",
            name="ck_stakeholders_type",
        ),
        sa.CheckConstraint("influence_level BETWEEN 1 AND 5", name="ck_stakeholders_influence"),
        sa.CheckConstraint("impact_level BETWEEN 1 AND 5", name="ck_stakeholders_impact"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stakeholders_organization_id", "stakeholders", ["organization_id"])

    op.create_table(
        "organization_esg_topics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("priority BETWEEN 1 AND 5", name="ck_organization_esg_topics_priority"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["esg_topics.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "topic_id", name="uq_organization_esg_topics_organization_topic"),
    )
    op.create_index("ix_organization_esg_topics_organization_id", "organization_esg_topics", ["organization_id"])
    op.create_index("ix_organization_esg_topics_topic_id", "organization_esg_topics", ["topic_id"])

    esg_topics = sa.table(
        "esg_topics",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("pillar", sa.String),
        sa.column("description", sa.Text),
        sa.column("active", sa.Boolean),
    )
    op.bulk_insert(
        esg_topics,
        [
            {"code": "climate-change", "name": "Climate Change", "pillar": "E", "description": "Climate risks and resilience.", "active": True},
            {"code": "ghg-emissions", "name": "GHG Emissions", "pillar": "E", "description": "Greenhouse gas emissions.", "active": True},
            {"code": "energy", "name": "Energy", "pillar": "E", "description": "Energy consumption and efficiency.", "active": True},
            {"code": "water", "name": "Water", "pillar": "E", "description": "Water use and management.", "active": True},
            {"code": "waste", "name": "Waste", "pillar": "E", "description": "Waste generation and disposal.", "active": True},
            {"code": "air-quality", "name": "Air Quality", "pillar": "E", "description": "Air pollutant monitoring.", "active": True},
            {"code": "biodiversity", "name": "Biodiversity", "pillar": "E", "description": "Biodiversity impacts.", "active": True},
            {"code": "land-use", "name": "Land Use", "pillar": "E", "description": "Land use and soil impacts.", "active": True},
            {"code": "pollution", "name": "Pollution", "pillar": "E", "description": "Pollution prevention.", "active": True},
            {"code": "occupational-health-safety", "name": "Occupational Health & Safety", "pillar": "S", "description": "Worker health and safety.", "active": True},
            {"code": "diversity-inclusion", "name": "Diversity & Inclusion", "pillar": "S", "description": "Inclusion and equal opportunity.", "active": True},
            {"code": "human-rights", "name": "Human Rights", "pillar": "S", "description": "Human rights due diligence.", "active": True},
            {"code": "employee-development", "name": "Employee Development", "pillar": "S", "description": "Development and engagement.", "active": True},
            {"code": "community-relations", "name": "Community Relations", "pillar": "S", "description": "Local community engagement.", "active": True},
            {"code": "supply-chain", "name": "Supply Chain", "pillar": "S", "description": "Responsible supply chain.", "active": True},
            {"code": "ethics", "name": "Ethics", "pillar": "G", "description": "Ethical conduct.", "active": True},
            {"code": "compliance", "name": "Compliance", "pillar": "G", "description": "Regulatory compliance.", "active": True},
            {"code": "risk-management", "name": "Risk Management", "pillar": "G", "description": "Enterprise risk management.", "active": True},
            {"code": "data-privacy", "name": "Data Privacy", "pillar": "G", "description": "Personal data governance.", "active": True},
            {"code": "cybersecurity", "name": "Cybersecurity", "pillar": "G", "description": "Information security.", "active": True},
            {"code": "transparency", "name": "Transparency", "pillar": "G", "description": "Transparent disclosure.", "active": True},
            {"code": "corporate-governance", "name": "Corporate Governance", "pillar": "G", "description": "Governance structures and oversight.", "active": True},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_organization_esg_topics_topic_id", table_name="organization_esg_topics")
    op.drop_index("ix_organization_esg_topics_organization_id", table_name="organization_esg_topics")
    op.drop_table("organization_esg_topics")
    op.drop_index("ix_stakeholders_organization_id", table_name="stakeholders")
    op.drop_table("stakeholders")
    op.drop_table("esg_profiles")
    op.drop_index("ix_sites_city_id", table_name="sites")
    op.drop_index("ix_sites_organization_id", table_name="sites")
    op.drop_table("sites")
    op.drop_index("ix_esg_topics_pillar", table_name="esg_topics")
    op.drop_table("esg_topics")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
