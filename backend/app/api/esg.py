from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.city_repository import CityRepository
from app.repositories.esg_profile_repository import ESGProfileRepository
from app.repositories.esg_topic_repository import ESGTopicRepository
from app.repositories.indicator_repository import IndicatorRepository, IndicatorValueRepository
from app.repositories.materiality_repository import ImmutableAssessmentError, MaterialityRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.stakeholder_repository import StakeholderRepository
from app.schemas.esg import (
    ESGProfileResponse,
    ESGProfileUpdate,
    ESGTopicResponse,
    OrganizationCreate,
    OrganizationOverviewResponse,
    OrganizationResponse,
    OrganizationTopicCreate,
    OrganizationTopicResponse,
    OrganizationUpdate,
    SiteCreate,
    SiteResponse,
    StakeholderCreate,
    StakeholderResponse,
)
from app.schemas.esg_intelligence import (
    ESGIndicatorResponse,
    IndicatorValueResponse,
    MaterialityExternalEvidenceResponse,
    ProviderStatusResponse,
    SiteSyncResponse,
)
from app.schemas.materiality import (
    MaterialityAssessmentCreate,
    MaterialityAssessmentResponse,
    MaterialityAssessmentUpdate,
    MaterialityExplanationComponents,
    MaterialityExplanationResponse,
    MaterialityMatrixResponse,
    MaterialityWeightsResponse,
    StakeholderAssessmentInput,
    StakeholderAssessmentResponse,
)
from app.services.esg_data.evidence_service import EvidenceService
from app.services.esg_data.provider_service import ProviderRegistry, ProviderService
from app.services.materiality_service import IncompleteAssessmentError, MaterialityService

router = APIRouter(prefix="/esg", tags=["ESG"])


def _organization_or_404(repo: OrganizationRepository, organization_id: int):
    organization = repo.get_by_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organiza\u00e7\u00e3o n\u00e3o encontrada")
    return organization


def _assessment_or_404(
    repo: MaterialityRepository, organization_id: int, assessment_id: int
):
    assessment = repo.get(organization_id, assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avalia\u00e7\u00e3o n\u00e3o encontrada")
    return assessment


def _validate_stakeholders(
    repo: MaterialityRepository, organization_id: int, stakeholders: list[StakeholderAssessmentInput]
) -> None:
    for stakeholder in stakeholders:
        if not repo.stakeholder_belongs_to_organization(organization_id, stakeholder.stakeholder_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Stakeholder n\u00e3o pertence \u00e0 organiza\u00e7\u00e3o",
            )


def _site_or_404(repo: SiteRepository, site_id: int):
    site = repo.get_by_id(site_id)
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")
    return site


def _indicator_value_response(value) -> IndicatorValueResponse:
    ttl_by_provider = {provider.name: provider.ttl_seconds for provider in ProviderRegistry().all()}
    ttl = ttl_by_provider.get(value.source, 6 * 60 * 60)
    collected_at = value.collected_at
    if collected_at.tzinfo is None:
        collected_at = collected_at.replace(tzinfo=UTC)
    age_seconds = max(0.0, (datetime.now(UTC) - collected_at).total_seconds())
    freshness_score = round(max(0.0, 100 * (1 - age_seconds / (ttl * 4))), 2)
    freshness_status = "fresh" if age_seconds <= ttl else "aging" if age_seconds <= ttl * 4 else "stale"
    return IndicatorValueResponse(
        id=value.id,
        indicator=value.indicator,
        organization_id=value.organization_id,
        site_id=value.site_id,
        site_name=value.site.name if value.site else None,
        value=value.value,
        unit=value.unit,
        source=value.source,
        source_reference=value.source_reference,
        latitude=value.latitude,
        longitude=value.longitude,
        observed_at=value.observed_at,
        collected_at=value.collected_at,
        source_metadata=value.source_metadata,
        quality_score=value.quality_score,
        freshness_score=freshness_score,
        freshness_status=freshness_status,
        relevance_score=value.relevance_score,
        confidence_score=value.confidence_score,
    )


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    return OrganizationRepository(db).create(**payload.model_dump())


@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return OrganizationRepository(db).list_all()


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    return _organization_or_404(OrganizationRepository(db), organization_id)


@router.put("/organizations/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db)
):
    organization_repo = OrganizationRepository(db)
    organization = _organization_or_404(organization_repo, organization_id)
    return organization_repo.update(organization, **payload.model_dump(exclude_unset=True))


@router.post(
    "/organizations/{organization_id}/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED
)
def create_site(organization_id: int, payload: SiteCreate, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    if payload.city_id is not None and CityRepository(db).get_by_id(payload.city_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cidade n\u00e3o encontrada")
    return SiteRepository(db).create(organization_id, **payload.model_dump())


@router.get("/organizations/{organization_id}/sites", response_model=list[SiteResponse])
def list_sites(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return SiteRepository(db).list_by_organization(organization_id)


@router.put("/organizations/{organization_id}/profile", response_model=ESGProfileResponse)
def upsert_esg_profile(organization_id: int, payload: ESGProfileUpdate, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return ESGProfileRepository(db).upsert(organization_id, **payload.model_dump())


@router.get("/organizations/{organization_id}/profile", response_model=ESGProfileResponse)
def get_esg_profile(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    profile = ESGProfileRepository(db).get_by_organization(organization_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil ESG n\u00e3o encontrado")
    return profile


@router.post(
    "/organizations/{organization_id}/stakeholders",
    response_model=StakeholderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stakeholder(organization_id: int, payload: StakeholderCreate, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return StakeholderRepository(db).create(organization_id, **payload.model_dump())


@router.get("/organizations/{organization_id}/stakeholders", response_model=list[StakeholderResponse])
def list_stakeholders(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return StakeholderRepository(db).list_by_organization(organization_id)


@router.get("/topics", response_model=list[ESGTopicResponse])
def list_esg_topics(db: Session = Depends(get_db)):
    return ESGTopicRepository(db).list_active()


@router.get("/organizations/{organization_id}/topics", response_model=list[OrganizationTopicResponse])
def list_organization_topics(organization_id: int, db: Session = Depends(get_db)):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return ESGTopicRepository(db).list_by_organization(organization_id)


@router.post(
    "/organizations/{organization_id}/topics",
    response_model=OrganizationTopicResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_organization_topic(
    organization_id: int, payload: OrganizationTopicCreate, db: Session = Depends(get_db)
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    topic_repo = ESGTopicRepository(db)
    if topic_repo.get_topic(payload.topic_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tema ESG n\u00e3o encontrado")
    return topic_repo.create_or_update_link(
        organization_id, payload.topic_id, **payload.model_dump(exclude={"topic_id"})
    )


@router.get("/organizations/{organization_id}/overview", response_model=OrganizationOverviewResponse)
def get_organization_overview(organization_id: int, db: Session = Depends(get_db)):
    organization = _organization_or_404(OrganizationRepository(db), organization_id)
    sites = SiteRepository(db).list_by_organization(organization_id)
    stakeholders = StakeholderRepository(db).list_by_organization(organization_id)
    links = ESGTopicRepository(db).list_by_organization(organization_id)
    enabled_topics = [link for link in links if link.enabled]
    pillar_counts = {pillar: 0 for pillar in ("E", "S", "G")}
    for link in enabled_topics:
        pillar_counts[link.topic.pillar] += 1
    return OrganizationOverviewResponse(
        organization=organization.name,
        sites=len(sites),
        stakeholders=len(stakeholders),
        esg_topics=len(enabled_topics),
        environmental_topics=pillar_counts["E"],
        social_topics=pillar_counts["S"],
        governance_topics=pillar_counts["G"],
    )


@router.get("/indicators", response_model=list[ESGIndicatorResponse])
def list_indicators(category: str | None = None, db: Session = Depends(get_db)):
    return IndicatorRepository(db).list_definitions(category)


@router.get("/providers", response_model=list[ProviderStatusResponse])
def list_provider_statuses(db: Session = Depends(get_db)):
    return ProviderService(db).provider_statuses()


@router.get(
    "/organizations/{organization_id}/indicators",
    response_model=list[IndicatorValueResponse],
)
def list_organization_indicators(
    organization_id: int,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    values = IndicatorValueRepository(db).list_for_organization(organization_id, category)
    return [_indicator_value_response(value) for value in values]


@router.get("/sites/{site_id}/indicators", response_model=list[IndicatorValueResponse])
def list_site_indicators(site_id: int, category: str | None = None, db: Session = Depends(get_db)):
    _site_or_404(SiteRepository(db), site_id)
    values = IndicatorValueRepository(db).list_for_site(site_id, category)
    return [_indicator_value_response(value) for value in values]


@router.get("/sites/{site_id}/climate-risk", response_model=list[IndicatorValueResponse])
def get_site_climate_risk(site_id: int, db: Session = Depends(get_db)):
    _site_or_404(SiteRepository(db), site_id)
    values = IndicatorValueRepository(db).list_for_site(site_id, category="risk")
    return [_indicator_value_response(value) for value in values]


@router.get("/sites/{site_id}/air-quality", response_model=list[IndicatorValueResponse])
def get_site_air_quality(site_id: int, db: Session = Depends(get_db)):
    _site_or_404(SiteRepository(db), site_id)
    values = IndicatorValueRepository(db).list_for_site(site_id, category="air")
    return [_indicator_value_response(value) for value in values]


@router.get("/sites/{site_id}/energy", response_model=list[IndicatorValueResponse])
def get_site_energy(site_id: int, db: Session = Depends(get_db)):
    _site_or_404(SiteRepository(db), site_id)
    values = IndicatorValueRepository(db).list_for_site(site_id, category="energy")
    return [_indicator_value_response(value) for value in values]


@router.post("/sites/{site_id}/sync", response_model=SiteSyncResponse)
def sync_site_intelligence(site_id: int, db: Session = Depends(get_db)):
    site = _site_or_404(SiteRepository(db), site_id)
    results = ProviderService(db).sync_site(site)
    return SiteSyncResponse(site_id=site.id, results=results)


@router.post(
    "/organizations/{organization_id}/materiality",
    response_model=MaterialityAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_materiality_assessment(
    organization_id: int,
    payload: MaterialityAssessmentCreate,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    repository = MaterialityRepository(db)
    if not repository.topic_is_enabled(organization_id, payload.topic_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="O tema ESG deve estar ativo para a organiza\u00e7\u00e3o antes da avalia\u00e7\u00e3o",
        )
    if repository.exists_for_topic_and_year(organization_id, payload.topic_id, payload.reporting_year):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="J\u00e1 existe uma avalia\u00e7\u00e3o para este tema e ano de reporte",
        )
    _validate_stakeholders(repository, organization_id, payload.stakeholders)
    try:
        assessment = repository.create(
            organization_id=organization_id,
            topic_id=payload.topic_id,
            reporting_year=payload.reporting_year,
            impact=payload.impact.model_dump() if payload.impact else None,
            financial=payload.financial.model_dump() if payload.financial else None,
            stakeholders=[item.model_dump() for item in payload.stakeholders],
            evidences=[item.model_dump() for item in payload.evidences],
            status=payload.status,
        )
        if assessment.status == "completed":
            EvidenceService(db).link_existing_for_assessment(assessment)
            db.commit()
        return assessment
    except IncompleteAssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc


@router.get(
    "/organizations/{organization_id}/materiality",
    response_model=list[MaterialityAssessmentResponse],
)
def list_materiality_assessments(
    organization_id: int,
    reporting_year: int | None = None,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return MaterialityRepository(db).list_assessments(organization_id, reporting_year)


@router.get(
    "/organizations/{organization_id}/materiality/matrix",
    response_model=MaterialityMatrixResponse,
)
def get_materiality_matrix(
    organization_id: int,
    reporting_year: int | None = None,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    year, assessments = MaterialityRepository(db).matrix(organization_id, reporting_year)
    return {"reporting_year": year, "assessments": assessments}


@router.get(
    "/organizations/{organization_id}/materiality/priorities",
    response_model=list[MaterialityAssessmentResponse],
)
def get_materiality_priorities(
    organization_id: int,
    reporting_year: int | None = None,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    year, assessments = MaterialityRepository(db).matrix(organization_id, reporting_year)
    return assessments


@router.get(
    "/organizations/{organization_id}/materiality/{assessment_id}/explanation",
    response_model=MaterialityExplanationResponse,
)
def get_materiality_explanation(
    organization_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    assessment = _assessment_or_404(MaterialityRepository(db), organization_id, assessment_id)
    weights = MaterialityService().weights
    return MaterialityExplanationResponse(
        topic=assessment.topic.name,
        reporting_year=assessment.reporting_year,
        status=assessment.status,
        materiality_score=assessment.materiality_score,
        priority=assessment.priority_level,
        components=MaterialityExplanationComponents(
            impact=assessment.impact_score,
            financial=assessment.financial_score,
            stakeholder=assessment.stakeholder_score,
        ),
        impact_assessment=assessment.impact_assessment,
        financial_assessment=assessment.financial_assessment,
        stakeholder_assessments=assessment.stakeholder_assessments,
        evidences=assessment.evidences,
        weights=MaterialityWeightsResponse(
            impact=weights.impact,
            financial=weights.financial,
            stakeholder=weights.stakeholder,
        ),
    )


@router.get(
    "/materiality/{assessment_id}/evidence",
    response_model=list[MaterialityExternalEvidenceResponse],
)
def get_materiality_external_evidence(assessment_id: int, db: Session = Depends(get_db)):
    assessment = MaterialityRepository(db).get_any(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada")
    evidences = EvidenceService(db).list_for_assessment(assessment_id)
    return [
        MaterialityExternalEvidenceResponse(
            id=evidence.id,
            relevance=evidence.relevance,
            linked_at=evidence.created_at,
            indicator_value=_indicator_value_response(evidence.indicator_value),
        )
        for evidence in evidences
    ]


@router.get(
    "/organizations/{organization_id}/materiality/{assessment_id}",
    response_model=MaterialityAssessmentResponse,
)
def get_materiality_assessment(
    organization_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    return _assessment_or_404(MaterialityRepository(db), organization_id, assessment_id)


@router.put(
    "/organizations/{organization_id}/materiality/{assessment_id}",
    response_model=MaterialityAssessmentResponse,
)
def update_materiality_assessment(
    organization_id: int,
    assessment_id: int,
    payload: MaterialityAssessmentUpdate,
    db: Session = Depends(get_db),
):
    _organization_or_404(OrganizationRepository(db), organization_id)
    repository = MaterialityRepository(db)
    assessment = _assessment_or_404(repository, organization_id, assessment_id)
    try:
        updated = repository.update(
            assessment,
            impact=payload.impact.model_dump() if payload.impact else None,
            financial=payload.financial.model_dump() if payload.financial else None,
            evidences=[item.model_dump() for item in payload.evidences] if payload.evidences else None,
            status=payload.status,
        )
        if updated.status == "completed":
            EvidenceService(db).link_existing_for_assessment(updated)
            db.commit()
        return updated
    except ImmutableAssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IncompleteAssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc


@router.post(
    "/materiality/{assessment_id}/stakeholders",
    response_model=StakeholderAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_materiality_stakeholder_assessment(
    assessment_id: int,
    payload: StakeholderAssessmentInput,
    db: Session = Depends(get_db),
):
    repository = MaterialityRepository(db)
    assessment = repository.get_any(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avalia\u00e7\u00e3o n\u00e3o encontrada")
    if not repository.stakeholder_belongs_to_organization(
        assessment.organization_id, payload.stakeholder_id
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Stakeholder n\u00e3o pertence \u00e0 organiza\u00e7\u00e3o",
        )
    try:
        return repository.upsert_stakeholder_assessment(assessment, payload.model_dump())
    except ImmutableAssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/materiality/{assessment_id}/stakeholders",
    response_model=list[StakeholderAssessmentResponse],
)
def list_materiality_stakeholder_assessments(assessment_id: int, db: Session = Depends(get_db)):
    assessment = MaterialityRepository(db).get_any(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avalia\u00e7\u00e3o n\u00e3o encontrada")
    return assessment.stakeholder_assessments
