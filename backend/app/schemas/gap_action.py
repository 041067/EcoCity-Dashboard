"""Strict API contracts for the Sprint 9 Gap & Action Engine."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.esg import ESGTopicResponse
from app.schemas.esg_intelligence import ESGIndicatorResponse

GapSeverity = Literal["low", "medium", "high", "critical"]
TargetStatus = Literal["planned", "active", "achieved", "cancelled"]
RiskStatus = Literal["open", "mitigating", "resolved"]
OpportunityStatus = Literal["open", "in_progress", "realized", "dismissed"]
ActionStatus = Literal["planned", "in_progress", "blocked", "completed", "cancelled"]


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class TargetCreate(StrictSchema):
    topic_id: int = Field(gt=0)
    indicator_id: int = Field(gt=0)
    site_id: int | None = Field(default=None, gt=0)
    name: str = Field(min_length=2, max_length=200)
    baseline_value: float
    baseline_year: int = Field(ge=2000, le=2100)
    target_value: float
    target_year: int = Field(ge=2001, le=2100)
    status: TargetStatus = "active"
    description: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def target_must_follow_baseline(self):
        if self.target_year <= self.baseline_year:
            raise ValueError("target_year must be after baseline_year")
        return self


class TargetUpdate(StrictSchema):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    baseline_value: float | None = None
    baseline_year: int | None = Field(default=None, ge=2000, le=2100)
    target_value: float | None = None
    target_year: int | None = Field(default=None, ge=2001, le=2100)
    status: TargetStatus | None = None
    description: str | None = Field(default=None, max_length=4000)


class TargetResponse(StrictSchema):
    id: int
    organization_id: int
    site_id: int | None = None
    topic_id: int
    indicator_id: int
    name: str
    baseline_value: float
    baseline_year: int
    target_value: float
    target_year: int
    unit: str
    status: TargetStatus
    description: str | None = None
    direction: Literal["higher_is_better", "lower_is_better"]
    current_value: float | None = None
    progress_percentage: float | None = None
    tracking_status: Literal["on_track", "at_risk", "off_track", "achieved", "no_data"]
    topic: ESGTopicResponse
    indicator: ESGIndicatorResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GapResponse(StrictSchema):
    id: int
    organization_id: int
    site_id: int | None = None
    topic_id: int
    indicator_id: int
    target_id: int | None = None
    assessment_id: int | None = None
    gap_type: str
    severity: GapSeverity
    status: Literal["open", "resolved"]
    current_value: float
    target_value: float
    gap_value: float
    unit: str
    description: str
    source: str
    detected_at: datetime | None = None
    resolved_at: datetime | None = None
    topic: ESGTopicResponse
    indicator: ESGIndicatorResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RiskResponse(StrictSchema):
    id: int
    organization_id: int
    site_id: int | None = None
    topic_id: int
    indicator_value_id: int | None = None
    risk_type: str
    likelihood: int
    impact: int
    risk_score: float
    risk_level: GapSeverity
    description: str
    source: str
    status: RiskStatus
    topic: ESGTopicResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OpportunityResponse(StrictSchema):
    id: int
    organization_id: int
    site_id: int | None = None
    topic_id: int
    indicator_id: int | None = None
    indicator_value_id: int | None = None
    opportunity_type: str
    potential_impact: int
    feasibility: int
    opportunity_score: float
    priority: GapSeverity
    description: str
    evidence_reference: str | None = None
    status: OpportunityStatus
    topic: ESGTopicResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ActionTaskCreate(StrictSchema):
    title: str = Field(min_length=2, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None


class ActionTaskUpdate(StrictSchema):
    title: str | None = Field(default=None, min_length=2, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None
    status: ActionStatus | None = None


class ActionTaskResponse(StrictSchema):
    id: int
    action_plan_id: int
    title: str
    description: str | None = None
    status: ActionStatus
    due_date: date | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ActionPlanCreate(StrictSchema):
    topic_id: int = Field(gt=0)
    site_id: int | None = Field(default=None, gt=0)
    target_id: int | None = Field(default=None, gt=0)
    gap_id: int | None = Field(default=None, gt=0)
    risk_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=2, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    responsible_area: str | None = Field(default=None, max_length=160)
    due_date: date | None = None


class ActionPlanUpdate(StrictSchema):
    title: str | None = Field(default=None, min_length=2, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    responsible_area: str | None = Field(default=None, max_length=160)
    due_date: date | None = None
    status: ActionStatus | None = None


class ActionPlanResponse(StrictSchema):
    id: int
    organization_id: int
    site_id: int | None = None
    topic_id: int
    target_id: int | None = None
    gap_id: int | None = None
    risk_id: int | None = None
    title: str
    description: str | None = None
    priority: GapSeverity
    status: ActionStatus
    responsible_area: str | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    progress_percentage: float
    topic: ESGTopicResponse
    tasks: list[ActionTaskResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PriorityBreakdown(StrictSchema):
    materiality: float
    gap_severity: float
    risk: float
    evidence_confidence: float


class PriorityResponse(StrictSchema):
    topic_id: int
    topic: ESGTopicResponse
    site_id: int | None = None
    score: float
    priority: GapSeverity
    breakdown: PriorityBreakdown
    evidence_ids: list[int]
    explanation: str


class RiskMatrixCell(StrictSchema):
    likelihood: int
    impact: int
    risks: list[RiskResponse]


class AnalysisRunResponse(StrictSchema):
    run_id: str
    organization_id: int
    gaps_open: int
    risks_open: int
    opportunities_open: int
    created: dict[str, int]
    updated: dict[str, int]


class AuditEntryResponse(StrictSchema):
    id: int
    organization_id: int
    actor: str
    entity_type: str
    entity_id: int | None = None
    action: str
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    source: str
    created_at: datetime | None = None
