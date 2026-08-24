from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.esg_indicator import ESGIndicator
from app.models.indicator_value import IndicatorValue


class IndicatorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_definitions(self, category: str | None = None) -> list[ESGIndicator]:
        query = self.db.query(ESGIndicator).filter(ESGIndicator.active.is_(True))
        if category:
            query = query.filter(ESGIndicator.category == category)
        return query.order_by(ESGIndicator.category, ESGIndicator.name).all()

    def get_or_create(self, **data) -> ESGIndicator:
        indicator = self.db.query(ESGIndicator).filter(ESGIndicator.code == data["code"]).first()
        if indicator is None:
            indicator = ESGIndicator(**data)
            self.db.add(indicator)
            self.db.flush()
        return indicator


class IndicatorValueRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **data) -> IndicatorValue:
        value = IndicatorValue(**data)
        self.db.add(value)
        self.db.flush()
        return value

    def list_for_site(
        self,
        site_id: int,
        category: str | None = None,
        codes: list[str] | None = None,
        limit: int = 100,
    ) -> list[IndicatorValue]:
        query = (
            self.db.query(IndicatorValue)
            .options(joinedload(IndicatorValue.indicator), joinedload(IndicatorValue.site))
            .filter(IndicatorValue.site_id == site_id)
        )
        if category:
            query = query.join(IndicatorValue.indicator).filter(ESGIndicator.category == category)
        if codes:
            query = query.join(IndicatorValue.indicator).filter(ESGIndicator.code.in_(codes))
        return query.order_by(IndicatorValue.collected_at.desc(), IndicatorValue.id.desc()).limit(limit).all()

    def list_for_organization(
        self,
        organization_id: int,
        category: str | None = None,
        limit: int = 200,
    ) -> list[IndicatorValue]:
        query = (
            self.db.query(IndicatorValue)
            .options(joinedload(IndicatorValue.indicator), joinedload(IndicatorValue.site))
            .filter(IndicatorValue.organization_id == organization_id)
        )
        if category:
            query = query.join(IndicatorValue.indicator).filter(ESGIndicator.category == category)
        return query.order_by(IndicatorValue.collected_at.desc(), IndicatorValue.id.desc()).limit(limit).all()

    def has_fresh_provider_data(self, site_id: int, provider: str, ttl_seconds: int) -> bool:
        threshold = datetime.now(UTC) - timedelta(seconds=ttl_seconds)
        return (
            self.db.query(IndicatorValue.id)
            .filter(
                IndicatorValue.site_id == site_id,
                IndicatorValue.source == provider,
                IndicatorValue.collected_at >= threshold,
            )
            .first()
            is not None
        )

    def has_provider_data(self, site_id: int, provider: str) -> bool:
        return (
            self.db.query(IndicatorValue.id)
            .filter(IndicatorValue.site_id == site_id, IndicatorValue.source == provider)
            .first()
            is not None
        )

    def latest_for_site_codes(self, site_id: int, codes: list[str]) -> dict[str, IndicatorValue]:
        values = self.list_for_site(site_id, codes=codes, limit=500)
        latest: dict[str, IndicatorValue] = {}
        for value in values:
            latest.setdefault(value.indicator.code, value)
        return latest
