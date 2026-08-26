"""Strict, JSON-only contracts for the ESG AI Copilot."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.esg import ESGTopicResponse
from app.schemas.gap_action import ActionPlanResponse


class StrictAIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


Priority = Literal["low", "medium", "high", "critical"]
ReportType = Literal["executive", "materiality", "risk", "progress", "full_esg"]
RecommendationStatus = Literal["pending", "approved", "dismissed", "converted"]


class DataSufficiency(StrictAIModel):
    level: Literal["low", "medium", "high"]
    score: float = Field(ge=0, le=100)
    evidence_count: int = Field(ge=0)
    coverage_percentage: float = Field(ge=0, le=100)
    average_quality: float = Field(ge=0, le=100)
    missing: list[str]


class GroundedItem(StrictAIModel):
    title: str = Field(min_length=1, max_length=240)
    detail: str = Field(min_length=1, max_length=1600)
    topic_id: int | None = Field(default=None, gt=0)
    evidence_ids: list[str] = Field(default_factory=list, max_length=8)


class ExecutiveSummaryContent(StrictAIModel):
    overall_situation: str = Field(min_length=1, max_length=2400)
    critical_topics: list[GroundedItem] = Field(default_factory=list, max_length=8)
    key_risks: list[GroundedItem] = Field(default_factory=list, max_length=8)
    opportunities: list[GroundedItem] = Field(default_factory=list, max_length=8)
    targets_requiring_attention: list[GroundedItem] = Field(default_factory=list, max_length=8)
    recommended_priorities: list[GroundedItem] = Field(default_factory=list, max_length=8)
    data_limitations: list[str] = Field(default_factory=list, max_length=12)


class ESGReportContent(ExecutiveSummaryContent):
    materiality_analysis: str = Field(min_length=1, max_length=3000)
    risk_analysis: str = Field(min_length=1, max_length=3000)
    opportunity_analysis: str = Field(min_length=1, max_length=3000)
    target_analysis: str = Field(min_length=1, max_length=3000)
    current_action_plans: str = Field(min_length=1, max_length=3000)
    gaps_analysis: str = Field(min_length=1, max_length=3000)


class AIRecommendationDraft(StrictAIModel):
    topic_id: int = Field(gt=0)
    title: str = Field(min_length=2, max_length=240)
    rationale: str = Field(min_length=1, max_length=1800)
    expected_impact: str = Field(min_length=1, max_length=1200)
    time_horizon: Literal["immediate", "short_term", "medium_term", "long_term"]
    priority: Priority
    evidence_ids: list[str] = Field(default_factory=list, max_length=8)


class RecommendationGenerationContent(StrictAIModel):
    recommendations: list[AIRecommendationDraft] = Field(default_factory=list, max_length=12)
    data_limitations: list[str] = Field(default_factory=list, max_length=12)


class CopilotChatRequest(StrictAIModel):
    question: str = Field(min_length=2, max_length=1000)


class CopilotChatContent(StrictAIModel):
    answer: str = Field(min_length=1, max_length=3000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=10)
    limitations: list[str] = Field(default_factory=list, max_length=12)


class CreateAIReportRequest(StrictAIModel):
    report_type: ReportType = "full_esg"
    reporting_year: int | None = Field(default=None, ge=2000, le=2100)


class ESGReportResponse(StrictAIModel):
    id: int
    organization_id: int
    report_type: ReportType
    reporting_year: int
    status: Literal["completed", "failed"]
    content: ExecutiveSummaryContent | ESGReportContent
    data_sufficiency: DataSufficiency
    model: str
    prompt_version: str
    generated_at: datetime | None = None
    cached: bool = False


class AIRecommendationResponse(StrictAIModel):
    id: int
    organization_id: int
    topic_id: int
    topic: ESGTopicResponse
    title: str
    rationale: str
    expected_impact: str
    time_horizon: Literal["immediate", "short_term", "medium_term", "long_term"]
    priority: Priority
    evidence_ids: list[str]
    status: RecommendationStatus
    action_plan_id: int | None = None
    generated_at: datetime | None = None
    model: str
    prompt_version: str


class RecommendationsResponse(StrictAIModel):
    recommendations: list[AIRecommendationResponse]
    data_sufficiency: DataSufficiency
    cached: bool = False


class ApproveRecommendationRequest(StrictAIModel):
    responsible_area: str | None = Field(default=None, max_length=160)
    due_date: date | None = None


class RecommendationActionResponse(StrictAIModel):
    recommendation: AIRecommendationResponse
    action: ActionPlanResponse


class CopilotChatResponse(StrictAIModel):
    answer: str
    evidence_ids: list[str]
    limitations: list[str]
    data_sufficiency: DataSufficiency
    model: str
    prompt_version: str
