from sqlalchemy.orm import Session

from app.models.provider_sync_log import ProviderSyncLog


class ProviderSyncRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(self, **data) -> ProviderSyncLog:
        entry = ProviderSyncLog(**data)
        self.db.add(entry)
        self.db.flush()
        return entry

    def latest_by_provider(self) -> dict[str, ProviderSyncLog]:
        entries = self.db.query(ProviderSyncLog).order_by(ProviderSyncLog.created_at.desc()).all()
        latest: dict[str, ProviderSyncLog] = {}
        for entry in entries:
            latest.setdefault(entry.provider, entry)
        return latest
