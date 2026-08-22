from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.organization import Organization


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **data) -> Organization:
        try:
            organization = Organization(**data)
            self.db.add(organization)
            self.db.commit()
            self.db.refresh(organization)
            return organization
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to create organization")
            raise DatabaseException("Failed to create organization", exc) from exc

    def list_all(self) -> list[Organization]:
        try:
            return (
                self.db.query(Organization)
                .filter(Organization.is_active.is_(True))
                .order_by(Organization.name)
                .all()
            )
        except Exception as exc:
            logger.exception("Failed to list organizations")
            raise DatabaseException("Failed to list organizations", exc) from exc

    def get_by_id(self, organization_id: int) -> Organization | None:
        try:
            return (
                self.db.query(Organization)
                .filter(Organization.id == organization_id, Organization.is_active.is_(True))
                .first()
            )
        except Exception as exc:
            logger.exception("Failed to fetch organization %s", organization_id)
            raise DatabaseException("Failed to fetch organization", exc) from exc

    def update(self, organization: Organization, **data) -> Organization:
        try:
            for field, value in data.items():
                setattr(organization, field, value)
            self.db.commit()
            self.db.refresh(organization)
            return organization
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to update organization %s", organization.id)
            raise DatabaseException("Failed to update organization", exc) from exc
