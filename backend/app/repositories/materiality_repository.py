from sqlalchemy.orm import Session, joinedload, selectinload

from app.exceptions.database_exception import DatabaseException
from app.logs.logger import logger
from app.models.assessment_evidence import AssessmentEvidence
from app.models.financial_assessment import FinancialAssessment
from app.models.impact_assessment import ImpactAssessment
from app.models.materiality_assessment import MaterialityAssessment
from app.models.organization_esg_topic import OrganizationESGTopic
from app.models.stakeholder import Stakeholder
from app.models.stakeholder_assessment import StakeholderAssessment
from app.services.materiality_service import IncompleteAssessmentError, MaterialityService


class ImmutableAssessmentError(ValueError):
    """Completed annual assessments are immutable for auditability."""


class MaterialityRepository:
    def __init__(self, db: Session, service: MaterialityService | None = None) -> None:
        self.db = db
        self.service = service or MaterialityService()

    @staticmethod
    def _load_options():
        return (
            joinedload(MaterialityAssessment.topic),
            joinedload(MaterialityAssessment.impact_assessment),
            joinedload(MaterialityAssessment.financial_assessment),
            selectinload(MaterialityAssessment.stakeholder_assessments).joinedload(
                StakeholderAssessment.stakeholder
            ),
            selectinload(MaterialityAssessment.evidences),
        )

    def _get_query(self):
        return self.db.query(MaterialityAssessment).options(*self._load_options())

    def get(self, organization_id: int, assessment_id: int) -> MaterialityAssessment | None:
        try:
            return (
                self._get_query()
                .filter(
                    MaterialityAssessment.id == assessment_id,
                    MaterialityAssessment.organization_id == organization_id,
                )
                .first()
            )
        except Exception as exc:
            logger.exception("Failed to fetch materiality assessment %s", assessment_id)
            raise DatabaseException("Failed to fetch materiality assessment", exc) from exc

    def get_any(self, assessment_id: int) -> MaterialityAssessment | None:
        try:
            return self._get_query().filter(MaterialityAssessment.id == assessment_id).first()
        except Exception as exc:
            logger.exception("Failed to fetch materiality assessment %s", assessment_id)
            raise DatabaseException("Failed to fetch materiality assessment", exc) from exc

    def list_assessments(
        self, organization_id: int, reporting_year: int | None = None
    ) -> list[MaterialityAssessment]:
        try:
            query = self._get_query().filter(MaterialityAssessment.organization_id == organization_id)
            if reporting_year is not None:
                query = query.filter(MaterialityAssessment.reporting_year == reporting_year)
            return query.order_by(
                MaterialityAssessment.reporting_year.desc(),
                MaterialityAssessment.materiality_score.desc().nullslast(),
                MaterialityAssessment.id,
            ).all()
        except Exception as exc:
            logger.exception("Failed to list materiality assessments for organization %s", organization_id)
            raise DatabaseException("Failed to list materiality assessments", exc) from exc

    def topic_is_enabled(self, organization_id: int, topic_id: int) -> bool:
        return bool(
            self.db.query(OrganizationESGTopic.id)
            .filter(
                OrganizationESGTopic.organization_id == organization_id,
                OrganizationESGTopic.topic_id == topic_id,
                OrganizationESGTopic.enabled.is_(True),
            )
            .first()
        )

    def stakeholder_belongs_to_organization(self, organization_id: int, stakeholder_id: int) -> bool:
        return bool(
            self.db.query(Stakeholder.id)
            .filter(Stakeholder.id == stakeholder_id, Stakeholder.organization_id == organization_id)
            .first()
        )

    def exists_for_topic_and_year(self, organization_id: int, topic_id: int, reporting_year: int) -> bool:
        return bool(
            self.db.query(MaterialityAssessment.id)
            .filter(
                MaterialityAssessment.organization_id == organization_id,
                MaterialityAssessment.topic_id == topic_id,
                MaterialityAssessment.reporting_year == reporting_year,
            )
            .first()
        )

    def create(
        self,
        organization_id: int,
        topic_id: int,
        reporting_year: int,
        impact: dict | None,
        financial: dict | None,
        stakeholders: list[dict],
        evidences: list[dict],
        status: str,
    ) -> MaterialityAssessment:
        try:
            assessment = MaterialityAssessment(
                organization_id=organization_id,
                topic_id=topic_id,
                reporting_year=reporting_year,
                status=status,
            )
            if impact is not None:
                assessment.impact_assessment = ImpactAssessment(**impact)
            if financial is not None:
                assessment.financial_assessment = FinancialAssessment(**financial)
            assessment.stakeholder_assessments = [StakeholderAssessment(**item) for item in stakeholders]
            assessment.evidences = [AssessmentEvidence(**item) for item in evidences]
            self.db.add(assessment)
            self.db.flush()
            self.service.calculate_assessment(assessment)
            if status == "completed":
                self.service.ensure_completable(assessment)
            self.db.commit()
            return self.get(organization_id, assessment.id)  # type: ignore[return-value]
        except IncompleteAssessmentError:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to create materiality assessment for organization %s", organization_id)
            raise DatabaseException("Failed to create materiality assessment", exc) from exc

    def update(
        self,
        assessment: MaterialityAssessment,
        impact: dict | None,
        financial: dict | None,
        evidences: list[dict] | None,
        status: str | None,
    ) -> MaterialityAssessment:
        if assessment.status == "completed":
            raise ImmutableAssessmentError("Completed assessments cannot be changed")
        try:
            if impact is not None:
                if assessment.impact_assessment is None:
                    assessment.impact_assessment = ImpactAssessment(**impact)
                else:
                    for field, value in impact.items():
                        setattr(assessment.impact_assessment, field, value)
            if financial is not None:
                if assessment.financial_assessment is None:
                    assessment.financial_assessment = FinancialAssessment(**financial)
                else:
                    for field, value in financial.items():
                        setattr(assessment.financial_assessment, field, value)
            if evidences:
                assessment.evidences.extend(AssessmentEvidence(**item) for item in evidences)
            self.db.flush()
            self.service.calculate_assessment(assessment)
            if status == "completed":
                self.service.ensure_completable(assessment)
            if status is not None:
                assessment.status = status
            self.db.commit()
            return self.get(assessment.organization_id, assessment.id)  # type: ignore[return-value]
        except IncompleteAssessmentError:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to update materiality assessment %s", assessment.id)
            raise DatabaseException("Failed to update materiality assessment", exc) from exc

    def upsert_stakeholder_assessment(
        self, assessment: MaterialityAssessment, data: dict
    ) -> StakeholderAssessment:
        if assessment.status == "completed":
            raise ImmutableAssessmentError("Completed assessments cannot be changed")
        try:
            stakeholder_assessment = next(
                (
                    item
                    for item in assessment.stakeholder_assessments
                    if item.stakeholder_id == data["stakeholder_id"]
                ),
                None,
            )
            if stakeholder_assessment is None:
                stakeholder_assessment = StakeholderAssessment(**data)
                assessment.stakeholder_assessments.append(stakeholder_assessment)
            else:
                for field, value in data.items():
                    setattr(stakeholder_assessment, field, value)
            self.db.flush()
            self.service.calculate_assessment(assessment)
            self.db.commit()
            refreshed = self.get(assessment.organization_id, assessment.id)
            assert refreshed is not None
            return next(
                item
                for item in refreshed.stakeholder_assessments
                if item.stakeholder_id == data["stakeholder_id"]
            )
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to save stakeholder materiality assessment %s", assessment.id)
            raise DatabaseException("Failed to save stakeholder assessment", exc) from exc

    def matrix(self, organization_id: int, reporting_year: int | None) -> tuple[int | None, list[MaterialityAssessment]]:
        try:
            year = reporting_year
            if year is None:
                latest = (
                    self.db.query(MaterialityAssessment.reporting_year)
                    .filter(
                        MaterialityAssessment.organization_id == organization_id,
                        MaterialityAssessment.status == "completed",
                    )
                    .order_by(MaterialityAssessment.reporting_year.desc())
                    .first()
                )
                year = latest[0] if latest else None
            if year is None:
                return None, []
            assessments = (
                self._get_query()
                .filter(
                    MaterialityAssessment.organization_id == organization_id,
                    MaterialityAssessment.reporting_year == year,
                    MaterialityAssessment.status == "completed",
                    MaterialityAssessment.materiality_score.is_not(None),
                )
                .order_by(MaterialityAssessment.materiality_score.desc(), MaterialityAssessment.id)
                .all()
            )
            return year, assessments
        except Exception as exc:
            logger.exception("Failed to build materiality matrix for organization %s", organization_id)
            raise DatabaseException("Failed to build materiality matrix", exc) from exc
