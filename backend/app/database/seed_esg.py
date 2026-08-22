"""Idempotent development seed for the ESG foundation.

Run after ``alembic upgrade head`` with:
    python -m app.database.seed_esg
"""

from datetime import datetime

from app.database.session import SessionLocal
from app.models.esg_profile import ESGProfile
from app.models.esg_topic import ESGTopic
from app.models.organization import Organization
from app.models.organization_esg_topic import OrganizationESGTopic
from app.models.site import Site
from app.models.stakeholder import Stakeholder
from app.repositories.city_repository import CityRepository

DEMO_ORGANIZATION = "Eco Industries S.A."


def seed() -> None:
    with SessionLocal() as db:
        city_repo = CityRepository(db)
        cities = {
            "São Paulo": city_repo.get_or_create("São Paulo", "SP", -23.5505, -46.6333),
            "Curitiba": city_repo.get_or_create("Curitiba", "PR", -25.4290, -49.2671),
            "Recife": city_repo.get_or_create("Recife", "PE", -8.0476, -34.8770),
        }

        organization = db.query(Organization).filter(Organization.name == DEMO_ORGANIZATION).first()
        if organization is None:
            organization = Organization(
                name=DEMO_ORGANIZATION,
                organization_type="company",
                industry_sector="Indústria",
                document="00.000.000/0001-00",
                country="Brasil",
                state="SP",
                city="São Paulo",
                employee_count=1250,
                description="Organização demonstrativa para desenvolvimento do EcoCity ESG.",
            )
            db.add(organization)
            db.flush()

        if organization.esg_profile is None:
            db.add(
                ESGProfile(
                    organization_id=organization.id,
                    reporting_year=datetime.now().year,
                    environmental_enabled=True,
                    social_enabled=True,
                    governance_enabled=True,
                    esg_maturity_level="developing",
                    sustainability_strategy="Integrar dados ambientais e gestão ESG nas decisões operacionais.",
                )
            )

        sites = [
            ("Fábrica São Paulo", "factory", "São Paulo", 700, 24500.0),
            ("Centro Curitiba", "office", "Curitiba", 150, 3200.0),
            ("Unidade Recife", "warehouse", "Recife", 90, 8100.0),
        ]
        for name, site_type, city_name, employee_count, area_m2 in sites:
            exists = (
                db.query(Site)
                .filter(Site.organization_id == organization.id, Site.name == name)
                .first()
            )
            if exists is None:
                city = cities[city_name]
                db.add(
                    Site(
                        organization_id=organization.id,
                        name=name,
                        site_type=site_type,
                        city_id=city.id,
                        latitude=city.latitude,
                        longitude=city.longitude,
                        employee_count=employee_count,
                        area_m2=area_m2,
                    )
                )

        stakeholders = [
            ("Funcionários", "employees", 5, 5),
            ("Comunidade", "community", 4, 5),
            ("Clientes", "customers", 4, 4),
            ("Fornecedores", "suppliers", 3, 4),
            ("Governo", "government", 5, 4),
            ("Investidores", "investors", 5, 5),
        ]
        for name, stakeholder_type, influence, impact in stakeholders:
            exists = (
                db.query(Stakeholder)
                .filter(Stakeholder.organization_id == organization.id, Stakeholder.name == name)
                .first()
            )
            if exists is None:
                db.add(
                    Stakeholder(
                        organization_id=organization.id,
                        name=name,
                        stakeholder_type=stakeholder_type,
                        influence_level=influence,
                        impact_level=impact,
                    )
                )

        topic_codes = [
            "energy",
            "water",
            "ghg-emissions",
            "waste",
            "air-quality",
            "occupational-health-safety",
            "employee-development",
            "community-relations",
            "compliance",
            "ethics",
            "risk-management",
        ]
        topics = db.query(ESGTopic).filter(ESGTopic.code.in_(topic_codes)).all()
        if len(topics) != len(topic_codes):
            raise RuntimeError("Catálogo ESG ausente. Execute 'alembic upgrade head' antes do seed.")
        for topic in topics:
            exists = (
                db.query(OrganizationESGTopic)
                .filter(
                    OrganizationESGTopic.organization_id == organization.id,
                    OrganizationESGTopic.topic_id == topic.id,
                )
                .first()
            )
            if exists is None:
                db.add(
                    OrganizationESGTopic(
                        organization_id=organization.id,
                        topic_id=topic.id,
                        enabled=True,
                        priority=4,
                    )
                )
        db.commit()
        print(f"Seed ESG concluído para {organization.name}.")


if __name__ == "__main__":
    seed()
