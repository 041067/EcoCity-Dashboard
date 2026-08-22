from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.city import CityResponse

OrganizationType = Literal["company", "municipality", "public_agency", "university", "other"]
SiteType = Literal["headquarters", "factory", "warehouse", "office", "municipal_region", "other"]
StakeholderType = Literal[
    "employees", "customers", "suppliers", "investors", "government", "community", "environment", "partners", "other"
]
ESGMaturityLevel = Literal["initial", "developing", "structured", "advanced"]
ESGPillar = Literal["E", "S", "G"]


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    organization_type: OrganizationType
    industry_sector: str | None = Field(default=None, max_length=120)
    document: str | None = Field(default=None, max_length=40)
    country: str = Field(default="Brasil", min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    employee_count: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=4000)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    organization_type: OrganizationType | None = None
    industry_sector: str | None = Field(default=None, max_length=120)
    document: str | None = Field(default=None, max_length=40)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    employee_count: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=4000)


class OrganizationResponse(OrganizationCreate):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SiteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    site_type: SiteType
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    city_id: int | None = Field(default=None, gt=0)
    employee_count: int | None = Field(default=None, ge=0)
    area_m2: float | None = Field(default=None, ge=0)


class SiteResponse(SiteCreate):
    id: int
    organization_id: int
    city: CityResponse | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ESGProfileUpdate(BaseModel):
    reporting_year: int = Field(ge=2000, le=2100)
    environmental_enabled: bool = True
    social_enabled: bool = True
    governance_enabled: bool = True
    sustainability_strategy: str | None = Field(default=None, max_length=4000)
    esg_maturity_level: ESGMaturityLevel = "initial"


class ESGProfileResponse(ESGProfileUpdate):
    id: int
    organization_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StakeholderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    stakeholder_type: StakeholderType
    influence_level: int = Field(ge=1, le=5)
    impact_level: int = Field(ge=1, le=5)
    description: str | None = Field(default=None, max_length=4000)


class StakeholderResponse(StakeholderCreate):
    id: int
    organization_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ESGTopicResponse(BaseModel):
    id: int
    code: str
    name: str
    pillar: ESGPillar
    description: str | None = None
    active: bool

    model_config = ConfigDict(from_attributes=True)


class OrganizationTopicCreate(BaseModel):
    topic_id: int = Field(gt=0)
    enabled: bool = True
    priority: int = Field(default=3, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=4000)


class OrganizationTopicResponse(OrganizationTopicCreate):
    id: int
    organization_id: int
    topic: ESGTopicResponse
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationOverviewResponse(BaseModel):
    organization: str
    sites: int
    stakeholders: int
    esg_topics: int
    environmental_topics: int
    social_topics: int
    governance_topics: int
