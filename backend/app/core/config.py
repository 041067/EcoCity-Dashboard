
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///ecocity.db"
    GROQ_API_KEY: str | None = None
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
