from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ESGIndicatorResponse(BaseModel):
    id: int
    code: str
    name: str
    pillar: Literal["E", "S", "G"]
    category: str
    unit: str
    description: str | None = None
    source_type: str
    direction: Literal["higher_is_better", "lower_is_better"]
    active: bool

    model_config = ConfigDict(from_attributes=True)


class IndicatorValueResponse(BaseModel):
    id: int
    indicator: ESGIndicatorResponse
    organization_id: int
    site_id: int
    site_name: str | None = None
    value: float
    unit: str
    source: str
    source_reference: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    observed_at: datetime | None = None
    collected_at: datetime
    source_metadata: dict[str, Any] | None = None
    quality_score: float
    freshness_score: float
    freshness_status: Literal["fresh", "aging", "stale"]
    relevance_score: float
    confidence_score: float


class ProviderStatusResponse(BaseModel):
    name: str
    display_name: str
    status: Literal["unknown", "online", "degraded", "offline"]
    last_sync: datetime | None = None
    data_categories: list[str]
    priority: int
    last_message: str | None = None


class ProviderSyncItem(BaseModel):
    provider: str
    status: str
    cached: bool
    values_collected: int
    duration_ms: int | None = None
    message: str | None = None


class SiteSyncResponse(BaseModel):
    site_id: int
    results: list[ProviderSyncItem]


class MaterialityExternalEvidenceResponse(BaseModel):
    id: int
    relevance: str
    linked_at: datetime | None = None
    indicator_value: IndicatorValueResponse
