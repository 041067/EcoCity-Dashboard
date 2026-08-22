from sqlalchemy.orm import Session, joinedload

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.esg_topic import ESGTopic
from app.models.organization_esg_topic import OrganizationESGTopic


class ESGTopicRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[ESGTopic]:
        try:
            return (
                self.db.query(ESGTopic)
                .filter(ESGTopic.active.is_(True))
                .order_by(ESGTopic.pillar, ESGTopic.name)
                .all()
            )
        except Exception as exc:
            logger.exception("Failed to list ESG topics")
            raise DatabaseException("Failed to list ESG topics", exc) from exc

    def get_topic(self, topic_id: int) -> ESGTopic | None:
        try:
            return self.db.query(ESGTopic).filter(ESGTopic.id == topic_id, ESGTopic.active.is_(True)).first()
        except Exception as exc:
            logger.exception("Failed to fetch ESG topic %s", topic_id)
            raise DatabaseException("Failed to fetch ESG topic", exc) from exc

    def create_or_update_link(self, organization_id: int, topic_id: int, **data) -> OrganizationESGTopic:
        try:
            link = (
                self.db.query(OrganizationESGTopic)
                .filter(
                    OrganizationESGTopic.organization_id == organization_id,
                    OrganizationESGTopic.topic_id == topic_id,
                )
                .first()
            )
            if link is None:
                link = OrganizationESGTopic(organization_id=organization_id, topic_id=topic_id, **data)
                self.db.add(link)
            else:
                for field, value in data.items():
                    setattr(link, field, value)
            self.db.commit()
            return self.get_link(link.id)  # type: ignore[return-value]
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to save ESG topic %s for organization %s", topic_id, organization_id)
            raise DatabaseException("Failed to save organization ESG topic", exc) from exc

    def get_link(self, link_id: int) -> OrganizationESGTopic | None:
        try:
            return (
                self.db.query(OrganizationESGTopic)
                .options(joinedload(OrganizationESGTopic.topic))
                .filter(OrganizationESGTopic.id == link_id)
                .first()
            )
        except Exception as exc:
            logger.exception("Failed to fetch organization ESG topic %s", link_id)
            raise DatabaseException("Failed to fetch organization ESG topic", exc) from exc

    def list_by_organization(self, organization_id: int) -> list[OrganizationESGTopic]:
        try:
            return (
                self.db.query(OrganizationESGTopic)
                .options(joinedload(OrganizationESGTopic.topic))
                .filter(OrganizationESGTopic.organization_id == organization_id)
                .order_by(OrganizationESGTopic.priority.desc(), OrganizationESGTopic.id)
                .all()
            )
        except Exception as exc:
            logger.exception("Failed to list ESG topics for organization %s", organization_id)
            raise DatabaseException("Failed to list organization ESG topics", exc) from exc
