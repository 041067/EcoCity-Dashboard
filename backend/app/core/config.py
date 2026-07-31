from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///ecocity.db"
    GROQ_API_KEY: Optional[str] = None
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
