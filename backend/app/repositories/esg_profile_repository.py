from sqlalchemy.orm import Session

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.esg_profile import ESGProfile


class ESGProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_organization(self, organization_id: int) -> ESGProfile | None:
        try:
            return self.db.query(ESGProfile).filter(ESGProfile.organization_id == organization_id).first()
        except Exception as exc:
            logger.exception("Failed to fetch ESG profile for organization %s", organization_id)
            raise DatabaseException("Failed to fetch ESG profile", exc) from exc

    def upsert(self, organization_id: int, **data) -> ESGProfile:
        try:
            profile = self.get_by_organization(organization_id)
            if profile is None:
                profile = ESGProfile(organization_id=organization_id, **data)
                self.db.add(profile)
            else:
                for field, value in data.items():
                    setattr(profile, field, value)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to save ESG profile for organization %s", organization_id)
            raise DatabaseException("Failed to save ESG profile", exc) from exc
