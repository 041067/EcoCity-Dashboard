from sqlalchemy.orm import Session, joinedload

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.site import Site


class SiteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, organization_id: int, **data) -> Site:
        try:
            site = Site(organization_id=organization_id, **data)
            self.db.add(site)
            self.db.commit()
            return self.get_by_id(site.id)  # type: ignore[return-value]
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to create site for organization %s", organization_id)
            raise DatabaseException("Failed to create site", exc) from exc

    def get_by_id(self, site_id: int) -> Site | None:
        try:
            return self.db.query(Site).options(joinedload(Site.city)).filter(Site.id == site_id).first()
        except Exception as exc:
            logger.exception("Failed to fetch site %s", site_id)
            raise DatabaseException("Failed to fetch site", exc) from exc

    def list_by_organization(self, organization_id: int) -> list[Site]:
        try:
            return (
                self.db.query(Site)
                .options(joinedload(Site.city))
                .filter(Site.organization_id == organization_id)
                .order_by(Site.name)
                .all()
            )
        except Exception as exc:
            logger.exception("Failed to list sites for organization %s", organization_id)
            raise DatabaseException("Failed to list sites", exc) from exc
