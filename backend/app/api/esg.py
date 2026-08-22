from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.city_repository import CityRepository
from app.repositories.esg_profile_repository import ESGProfileRepository
from app.repositories.esg_topic_repository import ESGTopicRepository
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

router = APIRouter(prefix="/esg", tags=["ESG"])


def _organization_or_404(repo: OrganizationRepository, organization_id: int):
    organization = repo.get_by_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organiza\u00e7\u00e3o n\u00e3o encontrada")
    return organization


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
