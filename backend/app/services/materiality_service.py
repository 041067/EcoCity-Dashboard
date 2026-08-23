"""Deterministic, configurable calculations for the Materiality Engine.

Scores are never accepted from API clients.  This module receives only the
underlying 1--5 dimensions and derives every 0--100 result server-side.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from app.core.config import settings

SCALE_MIN = 1
SCALE_MAX = 5
SCORE_MIN = 0
SCORE_MAX = 100


class IncompleteAssessmentError(ValueError):
    """Raised when a caller attempts to complete an assessment without inputs."""


@dataclass(frozen=True)
class MaterialityWeights:
    impact: float
    financial: float
    stakeholder: float

    def __post_init__(self) -> None:
        if any(weight < 0 or weight > 1 for weight in self.__dict__.values()):
            raise ValueError("Materiality weights must be between 0 and 1")
        if abs(sum(self.__dict__.values()) - 1.0) > 0.000001:
            raise ValueError("Materiality weights must add up to 1.0")


class MaterialityService:
    """Calculates the documented Sprint 7 materiality methodology."""

    def __init__(self, weights: MaterialityWeights | None = None) -> None:
        self.weights = weights or MaterialityWeights(
            impact=settings.MATERIALITY_IMPACT_WEIGHT,
            financial=settings.MATERIALITY_FINANCIAL_WEIGHT,
            stakeholder=settings.MATERIALITY_STAKEHOLDER_WEIGHT,
        )

    @staticmethod
    def _validate_scale(values: Iterable[int]) -> list[int]:
        normalized = list(values)
        if not normalized:
            raise ValueError("At least one assessment value is required")
        if any(value < SCALE_MIN or value > SCALE_MAX for value in normalized):
            raise ValueError(f"Assessment values must be between {SCALE_MIN} and {SCALE_MAX}")
        return normalized

    @staticmethod
    def _validate_score(score: float) -> float:
        if score < SCORE_MIN or score > SCORE_MAX:
            raise ValueError("Component scores must be between 0 and 100")
        return score

    @classmethod
    def _normalize(cls, values: Iterable[int]) -> float:
        validated = cls._validate_scale(values)
        return round(sum(validated) / len(validated) / SCALE_MAX * SCORE_MAX, 2)

    def calculate_impact(
        self, severity: int, scope: int, likelihood: int, remediability: int
    ) -> float:
        return self._normalize((severity, scope, likelihood, remediability))

    def calculate_financial(
        self,
        revenue_impact: int,
        cost_impact: int,
        asset_impact: int,
        financing_impact: int,
        regulatory_impact: int,
    ) -> float:
        return self._normalize(
            (revenue_impact, cost_impact, asset_impact, financing_impact, regulatory_impact)
        )

    def calculate_stakeholder(self, assessments: Iterable[object]) -> float | None:
        """Consolidate every stakeholder's relevance, concern and influence equally."""
        values: list[int] = []
        for assessment in assessments:
            values.extend(
                (
                    int(assessment.relevance),
                    int(assessment.concern_level),
                    int(assessment.influence),
                )
            )
        return self._normalize(values) if values else None

    def calculate_materiality(
        self,
        impact_score: float | None,
        financial_score: float | None,
        stakeholder_score: float | None,
    ) -> float | None:
        if None in (impact_score, financial_score, stakeholder_score):
            return None
        impact = self._validate_score(float(impact_score))
        financial = self._validate_score(float(financial_score))
        stakeholder = self._validate_score(float(stakeholder_score))
        return round(
            impact * self.weights.impact
            + financial * self.weights.financial
            + stakeholder * self.weights.stakeholder,
            2,
        )

    @staticmethod
    def classify_priority(materiality_score: float | None) -> str | None:
        if materiality_score is None:
            return None
        if materiality_score < 0 or materiality_score > 100:
            raise ValueError("Materiality score must be between 0 and 100")
        if materiality_score < 40:
            return "low"
        if materiality_score < 60:
            return "medium"
        if materiality_score < 80:
            return "high"
        return "critical"

    def calculate_assessment(self, assessment: object) -> None:
        impact = getattr(assessment, "impact_assessment", None)
        financial = getattr(assessment, "financial_assessment", None)
        stakeholder_assessments = getattr(assessment, "stakeholder_assessments", [])
        assessment.impact_score = (
            self.calculate_impact(
                impact.severity, impact.scope, impact.likelihood, impact.remediability
            )
            if impact is not None
            else None
        )
        assessment.financial_score = (
            self.calculate_financial(
                financial.revenue_impact,
                financial.cost_impact,
                financial.asset_impact,
                financial.financing_impact,
                financial.regulatory_impact,
            )
            if financial is not None
            else None
        )
        assessment.stakeholder_score = self.calculate_stakeholder(stakeholder_assessments)
        assessment.materiality_score = self.calculate_materiality(
            assessment.impact_score, assessment.financial_score, assessment.stakeholder_score
        )
        assessment.priority_level = self.classify_priority(assessment.materiality_score)

    def ensure_completable(self, assessment: object) -> None:
        if getattr(assessment, "materiality_score", None) is None:
            raise IncompleteAssessmentError(
                "Impact, financial and at least one stakeholder assessment are required to complete."
            )
