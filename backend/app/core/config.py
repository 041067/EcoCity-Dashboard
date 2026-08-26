
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///ecocity.db"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    AI_TIMEOUT_SECONDS: float = Field(default=25, ge=3, le=60)
    AI_MAX_COMPLETION_TOKENS: int = Field(default=1400, ge=128, le=4096)
    AI_CONTEXT_MAX_CHARS: int = Field(default=14000, ge=4000, le=30000)
    AI_RATE_LIMIT_REQUESTS: int = Field(default=12, ge=1, le=100)
    AI_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=10, le=3600)
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
    OPENAQ_API_KEY: str | None = None
    OPENAQ_URL: str = "https://api.openaq.org/v3"
    NASA_POWER_URL: str = "https://power.larc.nasa.gov/api"
    INPE_FIRE_WFS_URL: str = "https://terrabrasilis.dpi.inpe.br/queimadas/geoserver/ows"
    INPE_FIRE_LAYER: str = "bdqueimadas2:focos"
    INPE_DETER_WFS_URL: str = "https://terrabrasilis.dpi.inpe.br/geoserver/deter-amz/wfs"
    INPE_DETER_LAYER: str = "deter-amz:deter_amz"
    INPE_ALERT_LOOKBACK_DAYS: int = Field(default=7, ge=1, le=31)
    INPE_ALERT_RADIUS_KM: int = Field(default=10, ge=1, le=100)
    ANEEL_DATASTORE_URL: str = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search"
    ANEEL_SIGA_RESOURCE_ID: str = "2f65a1b0-19b8-4360-8238-b34ab4693d55"
    ANEEL_MAX_RECORDS: int = Field(default=5000, ge=100, le=10000)
    ESG_PROVIDER_TIMEOUT_SECONDS: float = Field(default=10, ge=1, le=30)
    ENVIRONMENT: str = "development"
    MATERIALITY_IMPACT_WEIGHT: float = Field(default=0.40, ge=0, le=1)
    MATERIALITY_FINANCIAL_WEIGHT: float = Field(default=0.40, ge=0, le=1)
    MATERIALITY_STAKEHOLDER_WEIGHT: float = Field(default=0.20, ge=0, le=1)

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @model_validator(mode="after")
    def validate_materiality_weights(self) -> "Settings":
        total = (
            self.MATERIALITY_IMPACT_WEIGHT
            + self.MATERIALITY_FINANCIAL_WEIGHT
            + self.MATERIALITY_STAKEHOLDER_WEIGHT
        )
        if abs(total - 1.0) > 0.000001:
            raise ValueError("Materiality weights must add up to 1.0")
        return self


settings = Settings()
