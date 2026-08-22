from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.stakeholder import Stakeholder


class StakeholderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, organization_id: int, **data) -> Stakeholder:
        try:
            stakeholder = Stakeholder(organization_id=organization_id, **data)
            self.db.add(stakeholder)
            self.db.commit()
            self.db.refresh(stakeholder)
            return stakeholder
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to create stakeholder for organization %s", organization_id)
            raise DatabaseException("Failed to create stakeholder", exc) from exc

    def list_by_organization(self, organization_id: int) -> list[Stakeholder]:
        try:
            return (
                self.db.query(Stakeholder)
                .filter(Stakeholder.organization_id == organization_id)
                .order_by(Stakeholder.name)
                .all()
            )
        except Exception as exc:
            logger.exception("Failed to list stakeholders for organization %s", organization_id)
            raise DatabaseException("Failed to list stakeholders", exc) from exc
