from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.esg import ESGTopicResponse, StakeholderResponse

AssessmentStatus = Literal["draft", "in_review", "completed"]
PriorityLevel = Literal["low", "medium", "high", "critical"]
EvidenceType = Literal["manual", "internal_data", "external_data", "document", "stakeholder"]


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ImpactAssessmentInput(StrictInput):
    severity: int = Field(ge=1, le=5)
    scope: int = Field(ge=1, le=5)
    likelihood: int = Field(ge=1, le=5)
    remediability: int = Field(ge=1, le=5)


class ImpactAssessmentResponse(ImpactAssessmentInput):
    id: int
    materiality_assessment_id: int

    model_config = ConfigDict(from_attributes=True)


class FinancialAssessmentInput(StrictInput):
    revenue_impact: int = Field(ge=1, le=5)
    cost_impact: int = Field(ge=1, le=5)
    asset_impact: int = Field(ge=1, le=5)
    financing_impact: int = Field(ge=1, le=5)
    regulatory_impact: int = Field(ge=1, le=5)


class FinancialAssessmentResponse(FinancialAssessmentInput):
    id: int
    materiality_assessment_id: int

    model_config = ConfigDict(from_attributes=True)


class StakeholderAssessmentInput(StrictInput):
    stakeholder_id: int = Field(gt=0)
    relevance: int = Field(ge=1, le=5)
    concern_level: int = Field(ge=1, le=5)
    influence: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=4000)


class StakeholderAssessmentResponse(StakeholderAssessmentInput):
    id: int
    materiality_assessment_id: int
    stakeholder: StakeholderResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentEvidenceInput(StrictInput):
    evidence_type: EvidenceType
    source: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=4000)
    reference: str | None = Field(default=None, max_length=1000)


class AssessmentEvidenceResponse(AssessmentEvidenceInput):
    id: int
    materiality_assessment_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MaterialityAssessmentCreate(StrictInput):
    topic_id: int = Field(gt=0)
    reporting_year: int = Field(ge=2000, le=2100)
    impact: ImpactAssessmentInput | None = None
    financial: FinancialAssessmentInput | None = None
    stakeholders: list[StakeholderAssessmentInput] = Field(default_factory=list, max_length=100)
    evidences: list[AssessmentEvidenceInput] = Field(default_factory=list, max_length=100)
    status: AssessmentStatus = "draft"

    @model_validator(mode="after")
    def validate_unique_stakeholders(self) -> "MaterialityAssessmentCreate":
        stakeholder_ids = [assessment.stakeholder_id for assessment in self.stakeholders]
        if len(stakeholder_ids) != len(set(stakeholder_ids)):
            raise ValueError("A stakeholder can only be assessed once per materiality assessment")
        return self


class MaterialityAssessmentUpdate(StrictInput):
    impact: ImpactAssessmentInput | None = None
    financial: FinancialAssessmentInput | None = None
    evidences: list[AssessmentEvidenceInput] | None = Field(default=None, max_length=100)
    status: AssessmentStatus | None = None


class MaterialityAssessmentResponse(BaseModel):
    id: int
    organization_id: int
    topic_id: int
    reporting_year: int
    impact_score: float | None
    financial_score: float | None
    stakeholder_score: float | None
    materiality_score: float | None
    priority_level: PriorityLevel | None
    status: AssessmentStatus
    topic: ESGTopicResponse
    impact_assessment: ImpactAssessmentResponse | None
    financial_assessment: FinancialAssessmentResponse | None
    stakeholder_assessments: list[StakeholderAssessmentResponse]
    evidences: list[AssessmentEvidenceResponse]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MaterialityMatrixItem(BaseModel):
    id: int
    topic: ESGTopicResponse
    reporting_year: int
    impact_score: float
    financial_score: float
    stakeholder_score: float
    materiality_score: float
    priority_level: PriorityLevel

    model_config = ConfigDict(from_attributes=True)


class MaterialityMatrixResponse(BaseModel):
    reporting_year: int | None
    assessments: list[MaterialityMatrixItem]


class MaterialityExplanationComponents(BaseModel):
    impact: float | None
    financial: float | None
    stakeholder: float | None


class MaterialityWeightsResponse(BaseModel):
    impact: float
    financial: float
    stakeholder: float


class MaterialityExplanationResponse(BaseModel):
    topic: str
    reporting_year: int
    status: AssessmentStatus
    materiality_score: float | None
    priority: PriorityLevel | None
    components: MaterialityExplanationComponents
    impact_assessment: ImpactAssessmentResponse | None
    financial_assessment: FinancialAssessmentResponse | None
    stakeholder_assessments: list[StakeholderAssessmentResponse]
    evidences: list[AssessmentEvidenceResponse]
    weights: MaterialityWeightsResponse
