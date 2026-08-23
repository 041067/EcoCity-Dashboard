
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///ecocity.db"
    GROQ_API_KEY: str | None = None
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
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
